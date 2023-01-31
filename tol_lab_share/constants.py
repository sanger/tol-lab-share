RABBITMQ_SUBJECT_CREATE_LABWARE = "create-labware"
RABBITMQ_SUBJECT_UPDATE_LABWARE = "update-labware"
RABBITMQ_FEEDBACK_EXCHANGE = "psd.tol"
RABBITMQ_ROUTING_KEY_CREATE_LABWARE_FEEDBACK = "feedback.created.labware"
RABBITMQ_ROUTING_KEY_UPDATE_LABWARE_FEEDBACK = "feedback.updated.labware"
RABBITMQ_SUBJECT_CREATE_LABWARE_FEEDBACK = "create-labware-feedback"
RABBITMQ_SUBJECT_UPDATE_LABWARE_FEEDBACK = "update-labware-feedback"

INPUT_CREATE_LABWARE_MESSAGE_MESSAGE_UUID = "messageUuid"
INPUT_CREATE_LABWARE_MESSAGE_CREATED_DATE_UTC = "messageCreateDateUtc"
INPUT_CREATE_LABWARE_MESSAGE_LABWARE = "labware"
INPUT_CREATE_LABWARE_MESSAGE_LABWARE_TYPE = "labwareType"
INPUT_CREATE_LABWARE_MESSAGE_BARCODE = "barcode"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLES = "samples"
INPUT_CREATE_LABWARE_MESSAGE_UUID = "labwareUuid"

INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_PUBLIC_NAME = "publicName"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COMMON_NAME = "commonName"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_CONCENTRATION = "concentration"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COUNTRY_OF_ORIGIN = "countryOfOrigin"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_DONOR_ID = "donorId"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_LABWARE_TYPE = "labwareType"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_LIBRARY_TYPE = "libraryType"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_LOCATION = "location"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_SAMPLE_ID = "sangerSampleId"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_TAXON_ID = "taxonId"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_SANGER_UUID = "sampleUuid"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_STUDY_UUID = "studyUuid"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_COLLECTION_DATE = "sampleCollectionDateUtc"
INPUT_CREATE_LABWARE_MESSAGE_SAMPLE_VOLUME = "volume"

OUTPUT_TRACTION_MESSAGE_CREATE_REQUEST_CONTAINER_TYPE_WELLS = "wells"
OUTPUT_TRACTION_MESSAGE_CREATE_REQUEST_CONTAINER_TYPE_TUBES = "tubes"
OUTPUT_TRACTION_MESSAGE_SOURCE = "tol-lab-share.tol"
