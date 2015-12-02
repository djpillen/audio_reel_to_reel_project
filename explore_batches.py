import os
from os.path import join
import pickle

cwd = os.getcwd()

batches_dir = 'R:/Digitization/Audio/Vendor Digitization/Reel-to-Reel Project'

batch_1 = join(batches_dir,'Batch 1/20130218')
batch_2 = join(batches_dir, 'Batch 2/20130716')
batch_3 = join(batches_dir, 'Batch 3/20140117')
batch_4 = join(batches_dir, 'Batch 4/20140826')

batches = {"Batch 1":batch_1, "Batch 2":batch_2, "Batch 3":batch_3, "Batch 4":batch_4}

batches_file = join(cwd,'batches.p')

expected_extensions = ['xml','jpg','wav','mp3','txt']

# Simple function to find the item number from a directory name to verify filenaming conventions, e.g. "0732-SR-1-1" returns "0732-SR-1"
def identify_item_number(item):
	item_split = item.split('-')
	item_number = '-'.join(item_split[:3])
	return item_number

def build_batch_dict(batch):
	collections = [item for item in os.listdir(batch) if os.path.isdir(join(batch,item))]
	collection_items = {}
	for collection in collections:
		collection_items[collection] = {}
		collection_dir = join(batch, collection)
		items = [item for item in os.listdir(collection_dir) if os.path.isdir(join(collection_dir,item))]
		for item in items:
			item_dir = join(collection_dir, item)
			collection_items[collection][item] = [filename for filename in os.listdir(item_dir) if not os.path.isdir(join(item_dir,filename))]
	return collection_items

if not os.path.exists(batches_file):
	print "Existing batches file not found."
	batches_dict = {}

	for batch in batches:
		print "Building dictionary for {0}".format(batch)
		batch_dir = batches[batch]
		batches_dict[batch] = build_batch_dict(batch_dir)

	with open(batches_file,'wb') as batches_file_out:
		print "Saving pickle file"
		pickle.dump(batches_dict, batches_file_out)
else:
	print "Existing batches file found"
	batches_dict = pickle.load(open(batches_file,'rb'))





"""
# Use this to find potential errors with files/filenaming.
# Leaving this here for reference, but it looks like everything is good

problematic_because_thumbs = []
problematic_because_misnamed_notes = []
problematic_because_multiple_notes = []
problematic_because_extensions = []	

for batch in batches_dict:
	batch_dir = batches[batch]
	for collection in batches_dict[batch]:
		for item in batches_dict[batch][collection]:
			item_number = identify_item_number(item)
			item_dir = join(batch_dir, collection, item)
			extensions = [filename.split('.')[-1] for filename in batches_dict[batch][collection][item]]
			unexpected_extensions = [extension for extension in extensions if extension not in expected_extensions]
			missing_extensions = [extension for extension in expected_extensions if extension not in extensions]
			if len(unexpected_extensions) > 0 or len(missing_extensions) > 0:
				problematic_because_extensions.append(item_dir)
			thumbs_db = [filename for filename in batches_dict[batch][collection][item] if filename == "Thumbs.db"]
			if thumbs_db:
				problematic_because_thumbs.append(item_dir)
			misnamed_notes = [filename for filename in batches_dict[batch][collection][item] if filename == "notes.txt"]
			if misnamed_notes:
				problematic_because_misnamed_notes.append(item_dir)
			notes_txt = [filename for filename in batches_dict[batch][collection][item] if filename.endswith('.txt')]
			if len(notes_txt) > 1:
				problematic_because_multiple_notes.append(item_dir)
			#for filename in batches_dict[batch][collection][item]:
				#if not filename.startswith(item_number) and not filename == "Thumbs.db":
					#print join(batch_dir, collection, item, filename)
					

unique_thumbs = [problem for problem in problematic_because_thumbs if problem not in problematic_because_extensions]
unique_notes = [problem for problem in problematic_because_misnamed_notes if problem not in problematic_because_extensions]
unique_extensions = [problem for problem in problematic_because_extensions if problem not in problematic_because_misnamed_notes and problem not in problematic_because_thumbs]

print "Unique thumbs:", unique_thumbs
print "Unique notes:", unique_notes
print "Unique extensions:", unique_extensions
print "Multiple notes:", problematic_because_multiple_notes
"""