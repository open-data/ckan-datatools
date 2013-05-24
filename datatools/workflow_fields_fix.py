import sys
import os
import ckanapi
#from jsonpath import jsonpath
from pprint import pprint 
import datatools
pending=['6789e638-b705-41ea-b0ca-430311cd8469',
 '53753f06-8b28-42d7-89f7-04cd014323b0',
 '95adb025-df39-4a74-b2d9-1e5bfb758201',
 '84de078c-c278-43ca-8217-14f4d2deb835',
 'c7affa02-e2c0-42cf-b78f-0dd12eb685d8',
 '53754205-1329-41f1-a205-4b462e6a11e5',
 '83564003-c70c-4775-a774-ca4f070db422',
 'cbfcbd36-eb28-4037-a2ae-39902faa1c29',
 '3ba64d8e-eedf-456b-8bfd-c178e0f9e577',
 'a42a7598-13c3-4226-be1d-499278a5b4a4',
 '6b90831e-d207-446e-bf67-1c0e0670c949',
 'c30e184d-8882-4085-8398-437369ed84c1',
 '4d7eb3ab-c2f3-4b24-8324-4d5294c883a7',
 '69249c7f-e565-41e3-85a4-2fa798c314b1',
 '6d795d98-1f58-4f02-b3b7-14b16450caa7',
 '20502beb-0349-4899-96b5-757fd97a2b12',
 '12be0672-3968-4cc8-a603-013ca5a93bb9',
 'cce93238-da31-40ec-bdf4-6b38adf2da4f',
 '6f08e9d8-cbb9-4428-9512-106c15d5289e',
 '774a50ac-a5e8-4502-8060-c83c81ceae05',
 '528b9df5-f583-4851-9306-f32806c1689b',
 'e8861339-d309-4d76-a898-f2749bc11a2b',
 '00cb41e1-9a97-4aba-b9b8-a8aaddef00ab',
 'ff5fc47a-f80f-441e-8851-8c5af1c07d19',
 'b5cd3d3f-1f2d-4cac-a2f9-194fa52ea6d3',
 'fd2d7ac0-ecdb-4f98-9102-738c43826658',
 '1cdcc939-5aff-45dc-8a5a-8ac17f5f2ab2',
 '8ddc1e3d-2b49-4e3d-a802-1d547f7e30f8',
 '10723cca-3b4b-4b9a-859d-c11c466898e8',
 '4cd42f68-09f7-4ee4-b599-309e823dca58',
 '5748d314-5b7a-4d93-a364-535ff716ff2c',
 '1e4b5073-f5ca-48bc-bfe5-792b8faf782d',
 '9caf35a1-f782-482a-80ed-18b3bdf86a43',
 '809ca694-22dc-4569-baaa-9339eb6a9837',
 'd14a3359-c21f-4fc0-a4d6-b3289401c9d6',
 '97028b79-c35e-4d22-98ae-adcb417cbbad',
 '964801d1-6591-474d-9a30-27ade861aaf3',
 '1eb57326-4bb6-4ef6-867d-cc574b64e19d',
 'e4897d94-151b-4978-9714-5bd034508af7',
 '3cbbcbd5-1865-4e4f-9b9c-e86f6d1e66a3',
 'c634685e-f771-4ca8-aeee-868e7c6bc2cf',
 'bdfbbff2-2872-448e-82c6-3d109294a048',
 'ca303a6a-11d2-401c-a172-af727bfe1476',
 '22546f7c-97e9-472e-979a-2c6551553ec1',
 '96c3fac7-df3f-4a95-bbde-ff755cb59af2',
 'b79d2426-28e5-47fb-b266-d9c78e2ca61c',
 '454c24f0-5a94-4293-9195-745d146868aa',
 '5f9a6fa1-9a09-4cdd-953d-c257bfc57c9c',
 'eb592806-fbc7-473e-b70e-2c3559beaab0',
 'ac92b054-1602-4f21-a0d6-1a5e75270454',
 '6e79c02f-2a6b-4904-815c-d74d4c5d8953',
 'a9777ec5-0dd9-42aa-8ab5-86ec839e9e70',
 '03d8d9ac-3a11-4566-9922-0559167cccac',
 'f7cd66e7-a213-40d1-9ce4-02432375c1bd',
 '981963a5-d771-4395-875e-86088073c8ef',
 '71559246-966d-44bf-89ff-33a2dc25cac4',
 '196ad7e2-9f7c-4d56-9795-5d7000cd13da']
def update_all_fields(ckansite):
    print "Working with data at  ", ckansite, ":    "
    pack_ids = datatools.registry_package_list()
    registry = ckanapi.RemoteCKAN('http://registry.statcan.gc.ca/')
    for i,pack_id in enumerate(pack_ids):
        # 1. Get the package
        pack = registry.action.package_show(id=pack_id)['result']
        pprint(pack['id'])
        pprint(pack['ready_to_publish'])
        #pprint(pack['portal_release_date'])
        # 2.  Update the fields
        pack['ready_to_publish']=True
        pack['portal_relase_date'] = '2013-05-24'
        if pack_id  in pending:
            pack['portal_relase_date'] = ''
        #pack['
        #pprint(pack['ready_to_publish'])
        # 3. Write the package
        resp = registry.action.package_update(**pack)
        # 4. Get the package as pack_after
        #print resp
        # 5. Check ensure evething is ok by comparing pack and pack_after
        '''
        for key, value in pack.items():
            print key
            if key == "resources": continue
            # deal with that pesky '\u2013' dash char
            #print key, (u"%s" % value).encode('utf8') 
        '''
        sys.exit() 
 

if __name__ == "__main__":
    #update_all_fields("http://data.statcan.gc.ca/data")
    update_all_fields("http://registry.statcan.gc.ca")
    #update_all_fields("http://localhost:5000")