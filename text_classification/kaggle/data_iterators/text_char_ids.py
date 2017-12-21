import sys
sys.path.append("../")
from overrides import overrides
import tensorflow as tf
from tc_utils.data_iterator import DataIterator
from tc_utils.feature_types import TextAndCharIdsFeature
from tc_utils.tf_hooks.data_initializers import IteratorInitializerHook

class TextAndCharIds(DataIterator):
    def __init__(self, batch_size):
        DataIterator.__init__(self)
        self.batch_size = batch_size

    def _setup_input_graph2(self,
                            word_ids,
                            char_ids,
                            labels,
                            batch_size,
                            is_eval=False,
                            shuffle=True,
                            scope='train_data'):
        """Return the input function to get the training audio_utils.

        Args:
            batch_size (int): Batch size of training iterator that is returned
                              by the input function.
            mnist_data (Object): Object holding the loaded mnist audio_utils.

        Returns:
            (Input function, IteratorInitializerHook):
                - Function that returns (features, labels) when called.
                - Hook to initialise input iterator.
        """
        iterator_initializer_hook = IteratorInitializerHook()

        tf.logging.info("text_features.shape: {}".format(word_ids.shape))
        tf.logging.info("numeric_features.shape: {}".format(char_ids.shape))
        tf.logging.info("labels.shape: {}".format(labels.shape))

        def inputs():
            """Returns training set as Operations.

            Returns:
                (features, labels) Operations that iterate over the dataset
                on every evaluation
            """
            with tf.name_scope(scope):

                # Define placeholders
                word_features_placeholder = tf.placeholder(tf.int32, word_ids.shape)
                char_features_placeholder = tf.placeholder(tf.int32, char_ids.shape)
                labels_placeholder = tf.placeholder(labels.dtype, labels.shape)

                # Build dataset iterator
                dataset = tf.data.Dataset.from_tensor_slices(({self.feature_type.FEATURE_1: word_features_placeholder,
                                                               self.feature_type.FEATURE_2: char_features_placeholder},
                                                              labels_placeholder))
                if is_eval:
                    dataset = dataset.repeat(1)
                else:
                    dataset = dataset.repeat(None)  # Infinite iterations

                if shuffle:
                    dataset = dataset.shuffle(buffer_size=10000)
                dataset = dataset.batch(batch_size)
                iterator = dataset.make_initializable_iterator()

                # Set runhook to initialize iterator
                iterator_initializer_hook.iterator_initializer_func = \
                    lambda sess: sess.run(
                        iterator.initializer,
                        feed_dict={word_features_placeholder: word_ids,
                                   char_features_placeholder: char_ids,
                                   labels_placeholder: labels})

                next_features, next_label = iterator.get_next()

                # Return batched (features, labels)
                return next_features, next_label

        # Return function and hook
        return inputs, iterator_initializer_hook

    def _test_inputs2(self, word_ids, char_ids, batch_size=1, scope='test_data'):
        """Returns test set as Operations.
        Returns:
            (features, ) Operations that iterate over the test set.
        """

        def inputs():
            with tf.name_scope(scope):
                word_ids_constant = tf.constant(word_ids, dtype=tf.int32)
                char_ids_constant = tf.constant(char_ids, dtype=tf.int32)
                dataset = tf.data.Dataset.from_tensor_slices(
                    ({self.feature_type.FEATURE_1: word_ids_constant, self.feature_type.FEATURE_2: char_ids_constant},))
                # Return as iteration in batches of 1
                return dataset.batch(batch_size).make_one_shot_iterator().get_next()

        return inputs

    @overrides
    def prepare(self,
                text_dataframe):

        self.feature_type = TextAndCharIdsFeature

        #To get text word ids
        train_text_word_ids = text_dataframe.get_train_text_word_ids()
        val_text_word_ids = text_dataframe.get_val_text_word_ids()
        test_text_word_ids = text_dataframe.get_test_text_word_ids()

        #To get text word char IDS
        train_text_word_char_ids = text_dataframe.get_train_text_word_char_ids()
        val_text_word_char_ids = text_dataframe.get_val_text_word_char_ids()
        test_text_word_char_ids = text_dataframe.get_test_text_word_char_ids()

        train_one_hot_encoded_label = text_dataframe.get_train_one_hot_label()
        val_one_hot_encoded_label= text_dataframe.get_val_one_hot_label()


        self.train_input_fn, self.train_input_hook = self._setup_input_graph2(train_text_word_ids,
                                                                              train_text_word_char_ids,
                                                                              train_one_hot_encoded_label,
                                                                              self.batch_size,
                                                                              is_eval=False,
                                                                              shuffle=True,
                                                                              scope='train_data')

        self.val_input_fn, self.val_input_hook= self._setup_input_graph2(val_text_word_ids,
                                                                         val_text_word_char_ids,
                                                                         val_one_hot_encoded_label,
                                                                         self.batch_size,
                                                                         is_eval=True,
                                                                         shuffle=True,
                                                                         scope='val_data')

        self.test_input_fn = self._test_inputs2(test_text_word_ids,
                                           test_text_word_char_ids,
                                           batch_size=1,
                                           scope='test_data')