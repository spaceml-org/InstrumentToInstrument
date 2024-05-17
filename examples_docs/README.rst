.. _iti_translation_index:

***********
Translation
***********

After training the ITI model, we can translate from one instrument to another, which offers the three use cases of image enhancement,
instrument intercalibration, and super-resolution observations. For the translation process we use the built-in translate function
located in the ``iti.translate`` directory. Here you find the the individual classes for the use cases.

If you want to translate your own data you can create a new translation class using the base class ``InstrumentToInstrument`` and implement the ``translate`` method.

=================================
Create custom translation classes
=================================

We show here an example to build you own translation class. We refer A to the source domain and B to the target domain.

.. code-block:: python

    class InstrumentAToInstrumentB(InstrumentToInstrument):
    def __init__(self, model_name='model name', **kwargs):
        super().__init__(model_name, **kwargs)
        self.norms = [['norm1'], ['norm2'], '...']

    def translate(self, path, basenames=None, **kwargs):
        A_dataset = ADataset(path, basenames=basenames, **kwargs)
        for maps, img, iti_img in self._translateDataset(A_dataset):
            yield [Map(norm.inverse((s_map.data + 1) / 2), self.toInstrumentBmeta(s_map.meta, instr))
                   for s_map, norm, instr in zip(maps, self.norms, ['InstrumentB'] * 2)]

    def toInstrumentBmeta(self, meta, instrument):
        wl_map = {174: 171, 304: 304}
        new_meta = meta.copy()
        new_meta['obsrvtry'] = 'ITI'
        new_meta['telescop'] = 'MissionB'
        new_meta['instrume'] = instrument
        new_meta['WAVELNTH'] = wl_map[meta.get('WAVELNTH', 0)]
        new_meta['waveunit'] = 'angstrom'
        return new_meta
