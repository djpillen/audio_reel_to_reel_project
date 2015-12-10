import csv
import os
from os.path import join
import pickle
import re

base_dir = os.getcwd()

# Point to pickle files
batches_file = join(base_dir,'batches.p')
beal_items_file = join(base_dir,'beal_items.p')
metadata_file = join(base_dir,'metadata.p')

# Open the ones that already exist
batches_dict = pickle.load(open(batches_file,'rb'))
beal_items_dict = pickle.load(open(beal_items_file,'rb'))

metadata_dict = {}

# The special_cases below represent files that do not conform to the standard digfilecalc regular expression result
# For the most part, these are single digfilecalcs that were split into multiple files due to size or other considerations
# This dictionary matches the result from the digfilecalc regular expression with the actual digfilecalc
special_cases = {
	'00135-SR-675-1-A':'00135-SR-675-1',
	'00135-SR-675-1-B':'00135-SR-675-1',
	'00135-SR-675-1-C':'00135-SR-675-1',
	'00135-SR-675-1-D':'00135-SR-675-1',
	'0601-SR-130-1-1':'0601-SR-130-1',
	'0601-SR-130-1-2':'0601-SR-130-2',
	'2010215-SR-7-1-1':'2010215-SR-7-1',
	'0648-SR-9-2-1-1':'0648-SR-9-2-1',
	'0648-SR-9-2-1-2':'0648-SR-9-2-1'
}

# Dictionary to match file extensions to mimetypes
mimetypes = {'mp3':'audio/mpeg3','wav':'audio/wav','txt':'text/plain','jpg':'image/jpeg','xml':'text/xml'}

# Dictionary to match file extensions to appropriate dc.description.filename content
description_filenames = {'txt':'Item Notes','xml':'METS XML','jpg':'Item Photo'}

# Identifies a collitemno for a given file by recursively stripping off the last '-[0-9]' from an item and comparing it against collitemnos from Beal until it gets a match
def find_collitemno(item):
	collitemno = False
	while not collitemno and len(item.split('-')) > 1:
		if item in beal_items_dict['items']:
			collitemno = item
		else:
			item = '-'.join(item.split('-')[:-1])
	return collitemno

for batch in batches_dict:
	for collection in batches_dict[batch]:
		for item in batches_dict[batch][collection]:
			photos = [filename for filename in batches_dict[batch][collection][item] if filename.endswith('jpg')]
			notes = [filename for filename in batches_dict[batch][collection][item] if filename.endswith('txt')]
			mets = [filename for filename in batches_dict[batch][collection][item] if filename.endswith('xml')]
			audio_files = [filename for filename in batches_dict[batch][collection][item] if filename.endswith('wav') or filename.endswith('mp3')]
			if len(audio_files) > 0:
				collitemno = find_collitemno(item)
				title = beal_items_dict['items'][collitemno]['title']
				itemdate = beal_items_dict['items'][collitemno]['itemdate']
				returndate = beal_items_dict['items'][collitemno]['returndate']
				collectioncreator = beal_items_dict['items'][collitemno]['collectioncreator']
				types = beal_items_dict['items'][collitemno]['types']
				metadata_dict[item] = {}
				metadata_dict[item]['photos'] = photos
				metadata_dict[item]['notes'] = notes
				metadata_dict[item]['mets'] = mets
				metadata_dict[item]['audio_files'] = audio_files
				metadata_dict[item]['title'] = title
				metadata_dict[item]['itemdate'] = itemdate
				metadata_dict[item]['returndate'] = returndate
				metadata_dict[item]['collectioncreator'] = collectioncreator
				metadata_dict[item]['collitemno'] = collitemno
				metadata_dict[item]['types'] = types

for item in metadata_dict:
	metadata_dict[item]['bitstreams'] = {}
	metadata_dict[item]['abstracts'] = []
	audio_bitstreams = metadata_dict[item]['audio_files']
	metadata_bitstreams = []
	metadata_bitstreams.extend(metadata_dict[item]['photos'])
	metadata_bitstreams.extend(metadata_dict[item]['notes'])
	metadata_bitstreams.extend(metadata_dict[item]['mets'])
	metadata_dict[item]['metadata_files'] = metadata_bitstreams
	for bitstream in audio_bitstreams:
		metadata_dict[item]['bitstreams'][bitstream] = {}
		extension = bitstream.split('.')[-1]
		digfilecalc = re.sub(r'\-?([A-Za-z]+)?\..*$','',bitstream)
		if digfilecalc in special_cases:
			digfilecalc = special_cases[digfilecalc]
		abstract = beal_items_dict['files'][digfilecalc]['abstract']
		if abstract not in metadata_dict[item]['abstracts']:
			metadata_dict[item]['abstracts'].append(abstract)
		metadata_dict[item]['bitstreams'][bitstream]['title'] = beal_items_dict['files'][digfilecalc]['title']
		metadata_dict[item]['bitstreams'][bitstream]['description_filename'] = beal_items_dict['files'][digfilecalc]['description_filename']
		metadata_dict[item]['bitstreams'][bitstream]['mimetype'] = mimetypes[extension]
	for bitstream in metadata_bitstreams:
		metadata_dict[item]['bitstreams'][bitstream] = {}
		extension = bitstream.split('.')[-1]
		metadata_dict[item]['bitstreams'][bitstream]['description_filename'] = description_filenames[extension]
		metadata_dict[item]['bitstreams'][bitstream]['mimetype'] = mimetypes[extension]
		
# Write the metadata dictionary
with open(metadata_file,'wb') as metadata_out:
	pickle.dump(metadata_dict,metadata_out)