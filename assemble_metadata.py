import pickle
import os
from os.path import join
from lxml import etree
import csv

base_dir = os.getcwd()

batches_file = join(base_dir,'batches.p')
beal_items_file = join(base_dir,'beal_items.p')