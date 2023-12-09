Configuration file
==================

An NLP pipeline config is a JSON file that contains one required element ``chainer``:

.. code:: python

    {
      "chainer": {
        "in": ["x"],
        "in_y": ["y"],
        "pipe": [
          ...
        ],
        "out": ["y_predicted"]
      }
    }

:class:`~deeppavlov.core.common.chainer.Chainer` is a core concept of DeepPavlov library: chainer builds a pipeline from
heterogeneous components (Rule-Based/ML/DL) and allows to train or infer from pipeline as a whole. Each component in the
pipeline specifies its inputs and outputs as arrays of names, for example: ``"in": ["tokens", "features"]`` and
``"out": ["token_embeddings", "features_embeddings"]`` and you can chain outputs of one components with inputs of other
components:

.. code:: python

    {
      "class_name": "deeppavlov.models.preprocessors.str_lower:str_lower",
      "in": ["x"],
      "out": ["x_lower"]
    },
    {
      "class_name": "nltk_tokenizer",
      "in": ["x_lower"],
      "out": ["x_tokens"]
    },

Pipeline elements could be child classes of :class:`~deeppavlov.core.models.component.Component` or functions.

Each :class:`~deeppavlov.core.models.component.Component` in the pipeline must implement method :meth:`__call__` and has
``class_name`` parameter, which is its registered codename, or full name of any python class in the form of
``"module_name:ClassName"``. It can also have any other parameters which repeat its :meth:`__init__` method arguments.
Default values of :meth:`__init__` arguments will be overridden with the config values during the initialization of a
class instance.

You can reuse components in the pipeline to process different parts of data with the help of ``id`` and ``ref``
parameters:

.. code:: python

    {
      "class_name": "nltk_tokenizer",
      "id": "tokenizer",
      "in": ["x_lower"],
      "out": ["x_tokens"]
    },
    {
      "ref": "tokenizer",
      "in": ["y"],
      "out": ["y_tokens"]
    },


Nested configuration files
--------------------------

Any configuration file could be used inside another configuration file as an element of the
:class:`~deeppavlov.core.common.chainer.Chainer` or as a field of another component using ``config_path`` key.
Any field of the nested configuration file could be overwritten using ``overwrite`` field:

.. code::

    "chainer": {
      "pipe": {
        ...
        {
          "class_name": "ner_chunk_model",
          "ner": {
            "config_path": "{CONFIGS_PATH}/ner/ner_ontonotes_bert.json",
            "overwrite": {
              "chainer.out": ["x_tokens", "tokens_offsets", "y_pred", "probas"]
            }
          },
          ...
        }
      }
    }

In this example ``ner_ontonotes_bert.json`` is used as ``ner`` argument value in ``ner_chunk_model`` component.
``chainer.out`` value is overwritten with new list. Overwritten fields names are defined using dot notation. In this
notation numeric fields are treated as indexes of lists. For example, to change ``class_name`` value of the second
element of the pipe to ``ner_chunker`` (1 is the index of the second element), use
``"chainer.pipe.1.class_name": "ner_chunker"`` key-value pair.


Variables
---------

As of *version 0.1.0* every string value in a configuration file is interpreted
as a `format string <https://docs.python.org/3.6/library/string.html#formatstrings>`__ where fields are evaluated
from ``metadata.variables`` element:

.. code:: python

    {
      "chainer": {
        "in": ["x"],
        "pipe": [
          {
            "class_name": "my_component",
            "in": ["x"],
            "out": ["x"],
            "load_path": "{MY_PATH}/file.obj"
          },
          {
            "in": ["x"],
            "out": ["y_predicted"],
            "config_path": "{CONFIGS_PATH}/classifiers/insults_kaggle_bert.json"
          }
        ],
        "out": ["y_predicted"]
      },
      "metadata": {
        "variables": {
          "MY_PATH": "/some/path",
          "CONFIGS_PATH": "{DEEPPAVLOV_PATH}/configs"
        }
      }
    }

Variable ``DEEPPAVLOV_PATH`` is always preset to be a path to the ``deeppavlov`` python module.

One can override configuration variables using environment variables with prefix ``DP_``. So environment variable
``DP_VARIABLE_NAME`` will override ``VARIABLE_NAME`` inside a configuration file.

For example, adding ``DP_ROOT_PATH=/my_path/to/large_hard_drive`` will make most configs use this path for downloading and reading  embeddings/models/datasets.

Training
--------

There are two abstract classes for trainable components: :class:`~deeppavlov.core.models.estimator.Estimator`
and :class:`~deeppavlov.core.models.nn_model.NNModel`.

:class:`~deeppavlov.core.models.estimator.Estimator` are fit once on any data with no batching or early stopping,
so it can be safely done at the time of pipeline initialization. :meth:`fit` method has to be implemented for each
:class:`~deeppavlov.core.models.estimator.Estimator`. One example is :class:`~deeppavlov.core.data.vocab.Vocab`.

:class:`~deeppavlov.core.models.nn_model.NNModel` requires more complex training. It can only be trained in a supervised
mode (as opposed to :class:`~deeppavlov.core.models.estimator.Estimator` which can be trained in both supervised and
unsupervised settings). This process takes multiple epochs with periodic validation and logging.
:meth:`~deeppavlov.core.models.nn_model.NNModel.train_on_batch` method has to be implemented for each
:class:`~deeppavlov.core.models.nn_model.NNModel`.

Training is triggered by :func:`~deeppavlov.train_model` function.


Train config
~~~~~~~~~~~~

:class:`~deeppavlov.core.models.estimator.Estimator` s that are trained should also have ``fit_on`` parameter which
contains a list of input parameter names. An :class:`~deeppavlov.core.models.nn_model.NNModel` should have the ``in_y``
parameter which contains a list of ground truth answer names. For example:

.. code:: python

    [
      {
        "id": "classes_vocab",
        "class_name": "default_vocab",
        "fit_on": ["y"],
        "level": "token",
        "save_path": "vocabs/classes.dict",
        "load_path": "vocabs/classes.dict"
      },
      {
        "in": ["x"],
        "in_y": ["y"],
        "out": ["y_predicted"],
        "class_name": "intent_model",
        "save_path": "classifiers/intent_cnn",
        "load_path": "classifiers/intent_cnn",
        "classes_vocab": {
          "ref": "classes_vocab"
        }
      }
    ]

The config for training the pipeline should have three additional elements: ``dataset_reader``, ``dataset_iterator``
and ``train``:

.. code:: python

    {
      "dataset_reader": {
        "class_name": ...,
        ...
      },
      "dataset_iterator": {
        "class_name": ...,
        ...
      },
      "chainer": {
        ...
      },
      "train": {
        ...
      }
    }


Simplified version of training pipeline contains two elements: ``dataset`` and ``train``. The ``dataset`` element
currently can be used for train from classification data in ``csv`` and ``json`` formats.


Train Parameters
~~~~~~~~~~~~~~~~

``train`` element can contain a ``class_name`` parameter that references a trainer class (default value is
:class:`torch_trainer <deeppavlov.core.trainers.torch_trainer.TorchTrainer>`).
All other parameters will be passed as keyword arguments to the trainer class's constructor.


Metrics
_______

.. code:: python

    "train": {
      "class_name": "torch_trainer",
      "metrics": [
        "f1",
        {
          "name": "accuracy",
          "inputs": ["y", "y_labels"]
        },
        {
          "name": "sklearn.metrics:accuracy_score",
          "alias": "unnormalized_accuracy",
          "inputs": ["y", "y_labels"],
          "normalize": false
        }
      ],
      ...
    }

The first metric in the list is used for early stopping.

Each metric can be described as a JSON object with ``name``, ``alias`` and ``inputs`` properties, where:

  - ``name`` is either a registered name of a metric function or ``module.submodules:function_name``.
  - ``alias`` is a metric name. Default value is ``name`` value.
  - ``inputs`` is a list of parameter names from chainer's inner memory that will be passed to the metric function.
    Default value is a concatenation of chainer's ``in_y`` and ``out`` parameters.

All other arguments are interpreted as kwargs when the metric is called.
If a metric is given as a string, this string is interpreted as a metric name, i.e. ``"f1"`` in the example
above is equivalent to ``{"name": "f1"}``.


DatasetReader
~~~~~~~~~~~~~

:class:`~deeppavlov.core.dara.dataset_reader.DatasetReader` class reads data and returns it in a specified format.
A concrete :class:`DatasetReader` class should be inherited from this base class and registered with a codename:


.. code:: python

    from deeppavlov.core.common.registry import register
    from deeppavlov.core.data.dataset_reader import DatasetReader

    @register('conll2003_reader')
    class Conll2003DatasetReader(DatasetReader):


DataLearningIterator and DataFittingIterator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`~deeppavlov.core.data.data_learning_iterator.DataLearningIterator` forms the sets of data ('train', 'valid',
'test') needed for training/inference and divides them into batches. A concrete :class:`DataLearningIterator` class
should be registered and can be inherited from :class:`deeppavlov.data.data_learning_iterator.DataLearningIterator`
class. This is a base class and can be used as a :class:`DataLearningIterator` as well.

:class:`~deeppavlov.core.data.data_fitting_iterator.DataFittingIterator` iterates over provided dataset without
train/valid/test splitting and is useful for :class:`~deeppavlov.core.models.estimator.Estimator` s that do not require
training.


Inference
---------

All components inherited from :class:`~deeppavlov.core.models.component.Component` abstract class can be used for
inference. The :meth:`__call__` method should return standard output of a component. For example, a `tokenizer`
should return `tokens`, a `NER recognizer` should return `recognized entities`, a `bot` should return an `utterance`.
A particular format of returned data should be defined in :meth:`__call__`.

Inference is triggered by :func:`~deeppavlov.core.commands.infer.interact_model` function. There is no need in a
separate JSON for inference.

Model Configuration
-------------------

Each DeepPavlov model is determined by its configuration file. You can use
existing config files or create yours. You can also choose a config file and 
modify preprocessors/tokenizers/embedders/vectorizers there. The components
below have the same interface and are responsible for the same functions,
therefore they can be used in the same parts of a config pipeline.

Here is a list of useful
:class:`~deeppavlov.core.models.component.Component`\ s aimed to preprocess,
postprocess and vectorize your data.

Preprocessors
~~~~~~~~~~~~~

Preprocessor is a component that processes batch of samples.

* Already implemented universal preprocessors of **tokenized texts** (each
  sample is a list of tokens):

    - :class:`~deeppavlov.models.preprocessors.mask.Mask` (registered as
      ``mask``) returns binary mask of corresponding length (padding up to the
      maximum length per batch.

    - :class:`~deeppavlov.models.preprocessors.sanitizer.Sanitizer`
      (registered as ``sanitizer``) removes all combining characters like
      diacritical marks from tokens.

* Already implemented universal preprocessors of **non-tokenized texts**
  (each sample is a string):

    - :class:`~deeppavlov.models.preprocessors.dirty_comments_preprocessor.DirtyCommentsPreprocessor`
      (registered as ``dirty_comments_preprocessor``) preprocesses samples
      converting samples to lowercase, paraphrasing English combinations with
      apostrophe ``'``,  transforming more than three the same symbols to two
      symbols.

    - :meth:`~deeppavlov.models.preprocessors.str_lower.str_lower` converts samples to lowercase.

* Already implemented universal preprocessors of another type of features:

    - :class:`~deeppavlov.models.preprocessors.one_hotter.OneHotter`
      (registered as ``one_hotter``) performs one-hotting operation for the
      batch of samples where each sample is an integer label or a list of
      integer labels (can be combined in one batch). If ``multi_label``
      parameter is set to ``True``, returns one one-dimensional vector per
      sample with several elements equal to ``1``.


Tokenizers
~~~~~~~~~~

Tokenizer is a component that processes batch of samples (each sample is a text
string).

    - :class:`~deeppavlov.models.tokenizers.nltk_tokenizer.NLTKTokenizer`
      (registered as ``nltk_tokenizer``) tokenizes using tokenizers from
      ``nltk.tokenize``, e.g. ``nltk.tokenize.wordpunct_tokenize``.

    - :class:`~deeppavlov.models.tokenizers.nltk_moses_tokenizer.NLTKMosesTokenizer`
      (registered as ``nltk_moses_tokenizer``) tokenizes and detokenizes using
      ``nltk.tokenize.moses.MosesDetokenizer``,
      ``nltk.tokenize.moses.MosesTokenizer``.

    - :class:`~deeppavlov.models.tokenizers.spacy_tokenizer.StreamSpacyTokenizer`
      (registered as ``stream_spacy_tokenizer``) tokenizes or lemmatizes texts
      with spacy ``en_core_web_sm`` models by default.

    - :class:`~deeppavlov.models.tokenizers.split_tokenizer.SplitTokenizer`
      (registered as ``split_tokenizer``) tokenizes using string method
      ``split``.


Embedders
~~~~~~~~~

Embedder is a component that converts every token in a tokenized batch to a
vector of a particular dimension (optionally, returns a single vector per
sample).

    - :class:`~deeppavlov.models.embedders.fasttext_embedder.FasttextEmbedder`
      (registered as ``fasttext``) reads embedding file in fastText format.
      If ``mean`` returns one vector per sample - mean of embedding vectors
      of tokens.

    - :class:`~deeppavlov.models.embedders.tfidf_weighted_embedder.TfidfWeightedEmbedder`
      (registered as ``tfidf_weighted``) accepts embedder, tokenizer (for
      detokenization, by default, detokenize with joining with space), TFIDF
      vectorizer or counter vocabulary, optionally accepts tags vocabulary (to
      assign additional multiplcative weights to particular tags). If ``mean``
      returns one vector per sample - mean of embedding vectors of tokens.

Vectorizers
~~~~~~~~~~~

Vectorizer is a component that converts batch of text samples to batch of
vectors.

    - :class:`~deeppavlov.models.sklearn.sklearn_component.SklearnComponent`
      (registered as ``sklearn_component``) is a DeepPavlov wrapper for most
      of sklearn estimators, vectorizers etc. For example, to get
      TFIDF-vectorizer one should assign in config ``model_class`` to
      ``sklearn.feature_extraction.text:TfidfVectorizer``, ``infer_method``
      to ``transform``, pass ``load_path``, ``save_path`` and other sklearn
      model parameters.

    - :class:`~deeppavlov.models.vectorizers.hashing_tfidf_vectorizer.HashingTfIdfVectorizer`
      (registered as ``hashing_tfidf_vectorizer``) implements hashing version
      of usual TFIDF-vecotrizer. It creates a TFIDF matrix from collection of
      documents of size ``[n_documents X n_features(hash_size)]``.

