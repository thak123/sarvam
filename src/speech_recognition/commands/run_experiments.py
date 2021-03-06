import argparse
from tqdm import tqdm
import tensorflow as tf
import sys
sys.path.extend(".")
from speech_recognition.commands.model_factory import ModelsFactory
from speech_recognition.commands.dataset_factory import DatasetFactory
from speech_recognition.commands.data_iterator_factory import DataIteratorFactory

from sarvam.helpers.print_helper import *
tf.logging.set_verbosity(tf.logging.INFO)
def run(opt):
    sess = tf.InteractiveSession()

    dataset = DatasetFactory.get(opt.dataset_name)
    dataset = dataset()

    data_iterator = DataIteratorFactory.get(opt.data_iterator_name)
    data_iterator = data_iterator(tf_sess=sess,
                                  num_epochs=opt.num_epochs,
                              batch_size=opt.batch_size,
                              audio_preprocessor=dataset)

    cfg, model = ModelsFactory.get(opt.model_name)

    # Get the model
    if opt.mode == "train":
        cfg = cfg.user_config()
    elif opt.mode == "retrain" or opt.mode == "predict":
        cfg = cfg.load(opt.model_dir)

    run_config = tf.ConfigProto()
    run_config.gpu_options.allow_growth = True
    # run_config.gpu_options.per_process_gpu_memory_fraction = 0.50
    run_config.allow_soft_placement = True
    run_config.log_device_placement = False
    run_config = tf.contrib.learn.RunConfig(session_config=run_config, model_dir=cfg._model_dir)


    model = model(cfg, run_config)

    if (model._feature_type != data_iterator._feature_type):
        raise Warning("Incompatible feature types between the model and data iterator")

    num_samples = dataset.NUM_SAMPLES
    batch_size = opt.batch_size

    if (opt.mode == "train" or opt.mode == "retrain"):
        # Evaluate after each epoch
        for current_epoch in tqdm(range(int(opt.num_epochs))):
            print_info("Training epoch: " + str(current_epoch + 1))
            tf.logging.info(CGREEN2 + str("Training epoch: " + str(current_epoch + 1)) + CEND)
            max_steps = (num_samples // batch_size) * (current_epoch + 1)

            model.train(input_fn=data_iterator.get_train_input_fn(),
                        hooks=[],
                        max_steps=max_steps) #5000 * 16 = 80000

            tf.logging.info(CGREEN2 + str("Evalution on epoch: " + str(current_epoch + 1)) + CEND)
            print_info("Evalution on epoch: " + str(current_epoch + 1))

            eval_results = model.evaluate(input_fn=data_iterator.get_val_input_fn(),
                                          hooks=[])

            tf.logging.info(CGREEN2 + str(str(eval_results)) + CEND)

    elif (opt.mode == "predict"):
        # Predict
        dataset.predict_on_csv_files(data_iterator, model)


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Run experiments on available models and datasets")


    optparse.add_argument('-mode', '--mode',
                          choices=['train', "retrain", "predict"],
                          required=True,
                          help="'preprocess, 'train', 'retrain','predict'"
                          )

    optparse.add_argument('-md', '--model-dir', action='store',
                          dest='model_dir', required=False,
                          help='Model directory needed for training')

    optparse.add_argument('-dsn', '--dataset-name', action='store',
                          dest='dataset_name', required=False,
                          help='Name of the Dataset to be used')

    optparse.add_argument('-din', '--data-iterator-name', action='store',
                          dest='data_iterator_name', required=False,
                          help='Name of the DataIterator to be used')

    optparse.add_argument('-bs', '--batch-size',  type=int, action='store',
                          dest='batch_size', required=False,
                          default=1,
                          help='Batch size for training, be consistent when retraining')

    optparse.add_argument('-ne', '--num-epochs', type=int, action='store',
                          dest='num_epochs', required=False,
                          help='Number of epochs')

    optparse.add_argument('-mn', '--model-name', action='store',
                          dest='model_name', required=False,
                          help='Name of the Model to be used')

    opt = optparse.parse_args()
    if (opt.mode == 'retrain' or opt.mode == 'predict') and not opt.model_dir:
        optparse.error('--model-dir argument is required in "retrain" & "predict" mode.')
    else:
        run(opt)