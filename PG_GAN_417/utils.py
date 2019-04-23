"""General utility functions"""
import os
import json
import logging
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import scipy.io as io
import torch

class Params():
    """Class that loads hyperparameters from a json file.

    Example:
    ```
    params = Params(json_path)
    print(params.learning_rate)
    params.learning_rate = 0.5  # change the value of learning_rate in params
    ```
    """

    def __init__(self, json_path):
        self.update(json_path)

    def save(self, json_path):
        """Saves parameters to json file"""
        with open(json_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def update(self, json_path):
        """Loads parameters from json file"""
        with open(json_path) as f:
            params = json.load(f)
            self.__dict__.update(params)

    @property
    def dict(self):
        """Gives dict-like access to Params instance by `params.dict['learning_rate']`"""
        return self.__dict__


def set_logger(log_path):
    """Sets the logger to log info in terminal and file `log_path`.

    In general, it is useful to have a logger so that every output to the terminal is saved
    in a permanent file. Here we save it to `model_dir/train.log`.

    Example:
    ```
    logging.info("Starting training...")
    ```

    Args:
        log_path: (string) where to log
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Logging to a file
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
        logger.addHandler(file_handler)

        # Logging to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(stream_handler)


def save_dict_to_json(d, json_path):
    """Saves dict of floats in json file

    Args:
        d: (dict) of float-castable values (np.float, int, float, etc.)
        json_path: (string) path to json file
    """
    with open(json_path, 'w') as f:
        # We need to convert the values to float for json (it doesn't accept np.array, np.float, )
        d = {k: float(v) for k, v in d.items()}
        json.dump(d, f, indent=4)


def row_csv2dict(csv_file):
    dict_club={}
    with open(csv_file)as f:
        reader=csv.reader(f,delimiter=',')
        for row in reader:
            dict_club[(row[0],row[1])]=row[2]
    return dict_club


def save_checkpoint(state, checkpoint):
    """Saves model and training parameters at checkpoint + 'last.pth.tar'. If is_best==True, also saves
    checkpoint + 'best.pth.tar'
    Args:
        state: (dict) contains model's state_dict, may contain other keys such as epoch, optimizer state_dict
        is_best: (bool) True if it is the best model seen till now
        checkpoint: (string) folder where parameters are to be saved
    """
    filepath = os.path.join(checkpoint, 'model.pth.tar')
    if not os.path.exists(checkpoint):
        print("Checkpoint Directory does not exist! Making directory {}".format(checkpoint))
        os.mkdir(checkpoint)
    else:
        print("Checkpoint Directory exists! ")
    torch.save(state, filepath)



def load_checkpoint(checkpoint, model, optimizer=None):
    """Loads model parameters (state_dict) from file_path. If optimizer is provided, loads state_dict of
    optimizer assuming it is present in checkpoint.
    Args:
        checkpoint: (string) filename which needs to be loaded
        model: (torch.nn.Module) model for which the parameters are loaded
        optimizer: (torch.optim) optional: resume optimizer from checkpoint
    """
    if not os.path.exists(checkpoint):
        raise("File doesn't exist {}".format(checkpoint))
    checkpoint = torch.load(checkpoint)
    iters = checkpoint['iters']
   # iters = 100000 
    generator, discriminator = model
    gen_loss_history = checkpoint['gen_loss_history']
    dis_loss_history = checkpoint['dis_loss_history']
    dis_loss_real_history = checkpoint['dis_loss_real_history']
    dis_loss_fake_history = checkpoint['dis_loss_fake_history']

    generator.load_state_dict(checkpoint['gen_state_dict'])
    discriminator.load_state_dict(checkpoint['dis_state_dict'])

    if optimizer:
        optim_G, optim_D = optimizer
        optim_G.load_state_dict(checkpoint['optim_G_state_dict'])
        optim_D.load_state_dict(checkpoint['optim_D_state_dict'])

    return iters,generator,discriminator, gen_loss_history, dis_loss_history,dis_loss_real_history,dis_loss_fake_history


def plot_loss_history(loss_history, output_dir):

    if len(loss_history) == 2:
        gen_loss_history, dis_loss_history = loss_history
        if gen_loss_history and dis_loss_history:
            pd.DataFrame({'generator': gen_loss_history, 'disciminator': dis_loss_history}).rolling(10).mean().plot()
            plt.savefig(output_dir + '/figures/history.png')
            history_path = os.path.join(output_dir,'history.mat')
            io.savemat(history_path, mdict={'gen_loss_history': gen_loss_history, 'dis_loss_history':dis_loss_history})
    else:
        gen_loss_history, dis_loss_history, Eff_history = loss_history
        if gen_loss_history and dis_loss_history:
            pd.DataFrame({'generator': gen_loss_history, 'disciminator': dis_loss_history}).rolling(10).mean().plot()
            plt.savefig(output_dir + '/figures/history.png')
            plt.figure()
            print(Eff_history)
            plt.plot(Eff_history)
            plt.ylabel('Avarage Efficiency')
            plt.xlabel('iteration/200')
            plt.savefig(output_dir + '/figures/Eff_history.png')
            history_path = os.path.join(output_dir,'history.mat')
            io.savemat(history_path, mdict={'gen_loss_history': gen_loss_history, 'dis_loss_history':dis_loss_history, 'Eff_history':Eff_history})


