QuickStart
------------

First, follow instructions on :doc:`Installation page </intro/installation>`
to install ``deeppavlov`` package for Python 3.6/3.7/3.8/3.9/3.10.

DeepPavlov contains a bunch of great pre-trained NLP models. Each model is
determined by its config file. List of models is available on
:doc:`the doc page </features/overview>` or in
the ``deeppavlov.configs``:

    .. code:: python
        
        from deeppavlov import configs

When you've decided on the model (+ config file), there are two ways to train,
evaluate and infer it:

* via `Command line interface (CLI)`_ and
* via `Python`_.

Before making choice of an interface, install model's package requirements
(CLI):

    .. code:: bash
        
        python -m deeppavlov install <config_path>

    * where ``<config_path>`` is model name without ``.json`` extension (e.g. ``insults_kaggle_bert``) or path to the
      chosen model's config file (e.g. ``deeppavlov/configs/classifiers/insults_kaggle_bert.json``)


Command line interface (CLI)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get predictions from a model interactively through CLI, run

    .. code:: bash
        
        python -m deeppavlov interact <config_path> [-d] [-i]

    * ``-d`` downloads required data -- pretrained model files and embeddings (optional).
    * ``-i`` installs model requirements (optional).

You can train it in the same simple way:

    .. code:: bash
        
        python -m deeppavlov train <config_path> [-d] [-i]

    Dataset will be downloaded regardless of whether there was ``-d`` flag or not.

    To train on your own data, you need to modify dataset reader path in the
    `train section doc <configuration.html#Train-config>`__. The data format is
    specified in the corresponding model doc page. 

There are even more actions you can perform with configs:

    .. code:: bash
        
        python -m deeppavlov <action> <config_path> [-d] [-i]

    * ``<action>`` can be
        * ``install`` to install model requirements (same as ``-i``),
        * ``download`` to download model's data (same as ``-d``),
        * ``train`` to train the model on the data specified in the config file,
        * ``evaluate`` to calculate metrics on the same dataset,
        * ``interact`` to interact via CLI,
        * ``riseapi`` to run a REST API server (see :doc:`docs
          </integrations/rest_api>`),
        * ``risesocket`` to run a socket API server (see :doc:`docs
          </integrations/socket_api>`),
        * ``predict`` to get prediction for samples from ``stdin`` or from
          ``<file_path>`` if ``-f <file_path>`` is specified.
    * ``<config_path>`` specifies path (or name) of model's config file
    * ``-d`` downloads required data
    * ``-i`` installs model requirements


Python
~~~~~~

To get predictions from a model interactively through Python, run

    .. code:: python
        
        from deeppavlov import build_model

        model = build_model(<config_path>, install=True, download=True)

        # get predictions for 'input_text1', 'input_text2'
        model(['input_text1', 'input_text2'])

where

    * ``install=True`` installs model requirements (optional),
    * ``download=True`` downloads required data from web -- pretrained model files and embeddings (optional),
    * ``<config_path>`` is path to the chosen model's config file (e.g.
      ``"deeppavlov/configs/ner/ner_ontonotes_bert_mult.json"``) or
      ``deeppavlov.configs`` attribute (e.g.
      ``deeppavlov.configs.ner.ner_ontonotes_bert_mult`` without quotation marks).

You can train it in the same simple way:

    .. code:: python
        
        from deeppavlov import train_model 

        model = train_model(<config_path>, install=True, download=True)

    * ``download=True`` downloads pretrained model, therefore the pretrained
      model will be, first, loaded and then trained (optional).

    Dataset will be downloaded regardless of whether there was ``-d`` flag or not.

    To train on your own data, you need to modify dataset reader path in the
    `train section doc <configuration.html#Train-config>`__. The data format is
    specified in the corresponding model doc page. 

You can also calculate metrics on the dataset specified in your config file:

    .. code:: python
        
        from deeppavlov import evaluate_model 

        model = evaluate_model(<config_path>, install=True, download=True)


Using GPU
~~~~~~~~~

To run or train **PyTorch**-based DeepPavlov models on GPU you should have `CUDA <https://developer.nvidia.com/cuda-toolkit>`__
installed on your host machine, and install model's package requirements. CUDA version should be compatible with
DeepPavlov :dp_file:`required PyTorch version <deeppavlov/requirements/pytorch.txt>`.

.. warning::
    If you use latest NVIDIA architecture, PyTorch installed from PyPI using DeepPavlov could not support your device
    CUDA capability. You will receive incompatible device warning after model initialization. You can install compatible
    package from `download.pytorch.org <https://download.pytorch.org/whl/torch_stable.html>`_. For example:

    .. code:: bash

        pip3 install torch==1.8.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html

If you want to run the code on GPU, just make the device visible for the script.
If you want to use a particular device, you may set it in command line:

    .. code:: bash

        export CUDA_VISIBLE_DEVICES=3; python -m deeppavlov train <config_path>

or in Python script:

    .. code:: python

        import os

        os.environ["CUDA_VISIBLE_DEVICES"]="3"

In case you want to keep GPU visible but disable GPU acceleration for specific component, use ``device`` paramenter
(available for :class:`~deeppavlov.core.models.torch_model.TorchModel` child classes): ``"device": "cpu"``.


Pretrained models
~~~~~~~~~~~~~~~~~

DeepPavlov provides a wide range of pretrained models.
See :doc:`features overview </features/overview>` for more info. Please
note that most of our models are trained on specific datasets for
specific tasks and may require further training on your data.
You can find a list of our out-of-the-box models `below <#out-of-the-box-pretrained-models>`_.


Docker images
~~~~~~~~~~~~~

You can run DeepPavlov models in :doc:`riseapi </integrations/rest_api>` mode or start Jupyter server
via Docker without installing DeepPavlov. Both your CPU and GPU (we support NVIDIA graphic
processors) can be utilised, please refer our `Docker <https://hub.docker.com/r/deeppavlov/deeppavlov>`_
images run instructions.


Out-of-the-box pretrained models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While the best way to solve most of the NLP tasks lies through collecting datasets
and training models according to the domain and an actual task itself, DeepPavlov
offers several pretrained models, which can be strong baselines for a wide range of tasks.

You can run these models `via Docker <#docker-images>`_ or in ``riseapi``/``risesocket`` mode to use in
solutions. See :doc:`riseapi </integrations/rest_api>` and :doc:`risesocket </integrations/socket_api>`
modes documentation for API details.


Text Question Answering
=======================

Text Question Answering component answers a question based on a given context (e.g,
a paragraph of text), where the answer to the question is a segment of the context.

.. table::
    :widths: auto

    +----------+------------------------------------------------------------------------------------+-------------------------------------------+
    | Language | DeepPavlov config                                                                  | Demo                                      |
    +==========+====================================================================================+===========================================+
    | En       | :config:`squad_bert <squad/squad_bert.json>`                                       | https://demo.deeppavlov.ai/#/en/textqa    |
    +----------+------------------------------------------------------------------------------------+-------------------------------------------+
    | Ru       | :config:`squad_ru_bert <squad/squad_ru_bert.json>`                                 | https://demo.deeppavlov.ai/#/ru/textqa    |
    +----------+------------------------------------------------------------------------------------+-------------------------------------------+


Name Entity Recognition
=======================

Named Entity Recognition (NER) classifies tokens in text into predefined categories
(tags), such as person names, quantity expressions, percentage expressions, names
of locations, organizations, as well as expression of time, currency and others.

.. table::
    :widths: auto

    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+
    | Language | DeepPavlov config                                                                              | Demo                                      |
    +==========+================================================================================================+===========================================+
    | Multi    | :config:`ner_ontonotes_bert_mult <ner/ner_ontonotes_bert_mult.json>`                           | https://demo.deeppavlov.ai/#/mu/ner       |
    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+
    | En       | :config:`ner_ontonotes_bert_mult <ner/ner_ontonotes_bert_mult.json>`                           | https://demo.deeppavlov.ai/#/en/ner       |
    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+
    | Ru       | :config:`ner_rus_bert <ner/ner_rus_bert.json>`                                                 | https://demo.deeppavlov.ai/#/ru/ner       |
    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+


Insult Detection
================

Insult detection predicts whether a text (e.g, post or speech in some
public discussion) is considered insulting to one of the persons it is
related to.

.. table::
    :widths: auto

    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+
    | Language | DeepPavlov config                                                                              | Demo                                      |
    +==========+================================================================================================+===========================================+
    | En       | :config:`insults_kaggle_bert <classifiers/insults_kaggle_bert.json>`                           | https://demo.deeppavlov.ai/#/en/insult    |
    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+


Paraphrase Detection
====================

Detect if two given texts have the same meaning.

.. table::
    :widths: auto

    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+
    | Language | DeepPavlov config                                                                              | Demo                                      |
    +==========+================================================================================================+===========================================+
    | Ru       | :config:`paraphraser_rubert <classifiers/paraphraser_rubert.json>`                             | None                                      |
    +----------+------------------------------------------------------------------------------------------------+-------------------------------------------+
