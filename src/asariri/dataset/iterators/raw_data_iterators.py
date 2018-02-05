from tqdm import tqdm
from sarvam.helpers.print_helper import *
import numpy as np
from scipy.io import wavfile
from tensorflow.contrib.learn.python.learn.learn_io.generator_io import generator_input_fn
import librosa
from PIL import Image
from asariri.dataset.features.asariri_features import AudioImageFeature
from asariri.dataset.crawled_data import CrawledData

class RawDataIterator:
    def __init__(self, batch_size, num_epochs, preprocessor):
        self._batch_size = batch_size
        self._num_epochs = num_epochs
        self._preprocessor = preprocessor
        self._feature_type = AudioImageFeature

    def melspectrogram(self, sample_rate, audio):
        mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=98, n_fft=1024, hop_length=2048) #3920 samples
        mfcc = mfcc.astype(np.float32)
        return mfcc.flatten()

    def data_generator(self, data, mode='train'):

        def generator():
            if mode == 'train':
                np.random.shuffle(data)

            batched_data_len = (len(data)//self._batch_size) * self._batch_size

            data_new = data[:batched_data_len]

            for i in tqdm(range(len(data_new)), desc=mode):
                data_dict  =data_new[i]
                audio_file_name = data_dict["audio"]
                image_file_name = data_dict["image"]
                person_name = data_dict["label"]


                if(i+1==batched_data_len):
                    raise StopIteration #Hack for the estimator from overshooting the iterator


                try:
                    sample_rate, wav = wavfile.read(audio_file_name)

                    wav = wav.astype(np.float32) / np.iinfo(np.int16).max

                    wav = self.melspectrogram(sample_rate=sample_rate, audio=wav)

                    if wav.shape[0] != 3920:
                        wav = np.pad(wav, (0, 3920 - wav.shape[0]), mode="constant", constant_values=(0,0))

                    image_data = Image.open(image_file_name)
                    image_data = np.array(image_data).astype(float)
                    image_data = np.expand_dims(image_data, axis=2)

                    # print_info("{} =====> {} {}".format(mode, audio_file_name, image_file_name))
                    # print_info("{} ===> {} {}".format(i, image_data.shape, wav.shape))
                    if(wav.shape[0] != 3920):
                        raise RuntimeWarning("{} has problematic shape {}".format(audio_file_name, wav.shape))

                except Exception as err:
                    print_error(str(err))

                yield {self._feature_type.FEATURE_AUDIO : wav,
                 self._feature_type.FEATURE_IMAGE: image_data }

        return generator

    def get_train_input_fn(self):
        train_input_fn = generator_input_fn(
            x=self.data_generator(self._preprocessor.get_train_files(), 'train'),
            target_key=self._feature_type.FEATURE_IMAGE,  # you could leave target_key in features, so labels in model_handler will be empty
            batch_size=self._batch_size,
            shuffle=True,
            num_epochs=1,
            queue_capacity=3 * self._batch_size + 10,
            num_threads=1,
        )

        return train_input_fn

    def get_val_input_fn(self):
        val_input_fn = generator_input_fn(
            x=self.data_generator(self._preprocessor.get_val_files(), 'val'),
            target_key=self._feature_type.FEATURE_IMAGE,
            batch_size=self._batch_size,
            shuffle=True,
            num_epochs=1,
            queue_capacity=3 * self._batch_size + 10,
            num_threads=1,
        )

        return val_input_fn

# preprocessor = CrawledData("../data/asariri/")
# iter = RawDataIterator(8,5,preprocessor)
# generator = iter.data_generator(preprocessor.get_train_files())
#
# for res in generator():
#     pass
#
# generator = iter.data_generator(preprocessor.get_val_files())
#
# for res in generator():
#     pass

