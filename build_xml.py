from lxml.builder import E
from lxml import etree
import os
from os.path import join
import pickle

base_dir = os.getcwd()

dspace_xml = join(base_dir,'dspace_xml')

metadata_file = join(base_dir,'metadata.p')

metadata_dict = pickle.load(open(metadata_file,'rb'))

for item in metadata_dict:
	print "Writing", item
	audio_item = E.audio_item(
		E("dc.identifier.other",item),
		E("dc.title", "Sound Recording - " + metadata_dict[item]['title'].decode('utf-8') + ' - ' + metadata_dict[item]['itemdate']),
		E("dc.contributor.author", metadata_dict[item]['collectioncreator']),
		E("dc.data.issued", "2015"),
		E("dc.date.created", metadata_dict[item]['returndate']),
		E("dc.coverage.temporal", metadata_dict[item]['itemdate'])
		)

	for dc_type in metadata_dict[item]['types']:
		audio_item.append(
			E("dc.type",dc_type)
			)

	audio_item.append(E("dc.rights.access","This material is available for research only in the Reading Room of the Bentley Historical Library at the University of Michigan (Ann Arbor, MI)."))
	audio_item.append(E("dc.rights.copyright","This recording may be protected by copyright law. Every audio, visual, or textual work has copyright protection unless that protection has expired over time or its creator has placed it in the public domain. It is the responsibility of anyone interested in reproducing, broadcasting or publishing content from the Bentley Historical Library collections to determine copyright holders and secure permissions accordingly."))
	audio_item.append(E("dc.date.open","2015"))
	audio_item.append(E("dc.description","Content note: The sound recording(s) associated with this repository item derive from a single audio reel tape. A single tape may yield multiple audio files if there were variations in tape stock, speed, or channels (i.e. stereo or mono). For more information see http://deepblue.lib.umich.edu/handle/2027.42/108126."))
	
	for abstract in metadata_dict[item]['abstracts']:
		audio_item.append(
			E("dc.abstract", abstract.decode('utf-8'))
			)

	for audio_file in metadata_dict[item]['audio_files']:
		audio_item.append(
			E.bitstream(
				E("dc.title.filename", audio_file),
				E("dc.description.filename", metadata_dict[item]['bitstreams'][audio_file]['description_filename'].decode('utf-8')),
				E("dc.format.mimetype", metadata_dict[item]['bitstreams'][audio_file]['mimetype'])
				)
			)

	for metadata_file in metadata_dict[item]['metadata_files']:
		audio_item.append(
			E.bitstream(
				E("dc.title.filename", metadata_file),
				E("dc.description.filename", metadata_dict[item]['bitstreams'][metadata_file]['description_filename']),
				E("dc.format.mimetype", metadata_dict[item]['bitstreams'][metadata_file]['mimetype'])
				)
			)

	with open(join(dspace_xml, item + '.xml'),'w') as xml_out:
		xml_out.write(etree.tostring(audio_item, encoding='utf-8', pretty_print=True))