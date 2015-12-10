import csv
import os
from os.path import join
import pickle
import re

base_dir = os.getcwd()

batches_dir = 'R:/Digitization/Audio/Vendor Digitization/Reel-to-Reel Project'

batches_file = join(base_dir,'batches.p')

batch_1_dir = join(batches_dir,'Batch 1/20130218')
batch_2_dir = join(batches_dir, 'Batch 2/20130716')
batch_3_dir = join(batches_dir, 'Batch 3/20140117')
batch_4_dir = join(batches_dir, 'Batch 4/20140826')

beal_exports_dir = join(base_dir,'BEAL_exports')

beal_items_file = join(base_dir,'beal_items.p')

batches = {"Batch 1":batch_1_dir, "Batch 2":batch_2_dir, "Batch 3":batch_3_dir, "Batch 4":batch_4_dir}

# Removes problematic bytes from a Beal exported CSV
def cleanup_beal_exports(export_dir):
	for filename in os.listdir(export_dir):
		exported = open(join(export_dir,filename),'rb')
		data = exported.read()
		exported.close()
		no_nulls = open(join(export_dir,filename),'wb')
		no_nulls.write(data.replace('\x00','').replace('\x0b',''))
		no_nulls.close()

# Assembles a dictionary for each batch like: [collection][item] = [files]
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

# Assembles a dictionary from Beal exported CSVs containing all required information
# Dictionary looks like: {'items':{collitemnos with item-level information}, 'files':{digfilecalcs with file-level information}}
def build_beal_dict(export_dir):
	print "Building Beal dictionary"
	beal_items_dict = {'files':{},'items':{}}
	for filename in os.listdir(export_dir):
		with open(join(export_dir,filename),'rb') as csvfile:
			reader = csv.reader(csvfile)
			next(reader,None)
			lastcollitemno = None
			for row in reader:
				if row[11]:
					collitemno = row[11].strip()
					lastcollitemno = collitemno
					collectioncreator = row[78].strip()
					audio_genre = row[51].strip()
					itemdate = row[23].strip()
					returndate = row[43].strip()
					description_filename_parts = []
					programno = row[38].strip()
					if programno:
						description_filename_parts.append('[Program ' + programno + ']')
					side = row[25].strip()
					if side:
						description_filename_parts.append('[Side ' + side + ']')
					part = row[27].strip()
					if part:
						description_filename_parts.append(part)
					segment = row[26]
					if segment:
						description_filename_parts.append('[Segment '+ segment + ']')
					description_filename = ' : '.join(description_filename_parts)
					title = row[29].decode('windows-1252').encode('utf-8').strip()
					notecontent = row[33].strip()
					if notecontent:
						abstract = description_filename + ' : ' + notecontent
					digfilecalc = row[15]
					beal_items_dict['files'][digfilecalc] = {'collitemno':collitemno,'title':title,'description_filename':description_filename.decode('windows-1252').encode('utf-8'),'abstract':abstract.decode('windows-1252').encode('utf-8')}
					if collitemno not in beal_items_dict['items']:
						beal_items_dict['items'][collitemno] = {'titles':[],'collectioncreator':collectioncreator,'digfilecalcs':[], 'itemdate':itemdate,'returndate':returndate,'types':[]}
					if title not in beal_items_dict['items'][collitemno]['titles']:
						beal_items_dict['items'][collitemno]['titles'].append(title)
					beal_items_dict['items'][collitemno]['digfilecalcs'].append(digfilecalc)
					beal_items_dict['items'][collitemno]['types'].append(audio_genre)
				else:
					if row[51]:
						audio_genre = row[51]
						collitemno = lastcollitemno
						beal_items_dict['items'][collitemno]['types'].append(audio_genre)
					
	with open(beal_items_file,'wb') as beal_file_out:
		pickle.dump(beal_items_dict,beal_file_out)
					
# Make a batches_dict and save it to a pickle file if it doesn't already exist
if not os.path.exists(batches_file):
	print "Existing batches file not found."
	batches_dict = {}

	for batch in batches:
		print "Building dictionary for {0}".format(batch)
		batch_dir = batches[batch]
		batches_dict[batch] = build_batch_dict(batch_dir)

	with open(batches_file,'wb') as batches_file_out:
		print "Saving batches file"
		pickle.dump(batches_dict, batches_file_out)
# Load the existing batches_dict from a pickle file if it does exist
else:
	print "Existing batches file found"
	batches_dict = pickle.load(open(batches_file,'rb'))

# Uncomment the below cleanup_beal_exports function call after exporting new CSVs to remove tricky bytes
#cleanup_beal_exports(beal_exports_dir)
build_beal_dict(beal_exports_dir)



'''
# Use this to find potential errors with files/filenaming.
# Leaving this here for reference, but it looks like everything is good

expected_extensions = ['xml','jpg','wav','mp3','txt']

issues_dir = join(base_dir,'issues')

thumbs_csv = join(issues_dir,'thumbs.csv')
misnamed_notes_csv = join(issues_dir,'misnamed_notes.csv')
multiple_notes_csv = join(issues_dir,'multiple_notes.csv')
extensions_csv = join(issues_dir,'extensions.csv')


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
			unexpected_extensions = [extension for extension in extensions if extension not in expected_extensions and extension != 'db']
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

def write_problem_csv(problem_list, problem_csv):
	with open(problem_csv,'ab') as csvfile:
		writer = csv.writer(csvfile)
		for item in problem_list:
			writer.writerow([item])

if problematic_because_thumbs:
	write_problem_csv(problematic_because_thumbs,thumbs_csv)
if problematic_because_extensions:
	write_problem_csv(problematic_because_extensions,extensions_csv)
if problematic_because_misnamed_notes:
	write_problem_csv(problematic_because_misnamed_notes,misnamed_notes_csv)
if problematic_because_multiple_notes:
	write_problem_csv(problematic_because_multiple_notes,multiple_notes_csv)

#unique_thumbs = [problem for problem in problematic_because_thumbs if problem not in problematic_because_extensions]
#unique_notes = [problem for problem in problematic_because_misnamed_notes if problem not in problematic_because_extensions]
#unique_extensions = [problem for problem in problematic_because_extensions if problem not in problematic_because_misnamed_notes and problem not in problematic_because_thumbs]

#print "Unique thumbs:", unique_thumbs
#print "Unique notes:", unique_notes
#print "Unique extensions:", unique_extensions
#print "Multiple notes:", problematic_because_multiple_notes
'''