# coding: utf8
db.define_table('client',
                Field('last_name', 'string'),
                Field('first_name','string'),
                Field('minst', 'string'),
                Field('address', 'string'),
                Field('zip', 'string'),
                Field('member_id', 'integer'),
                Field('stat','string'),
 #               auth.signature
                migrate = False)

db.define_table('case_action_master',
                Field('action_name'),
                Field('action_value'),
 #               auth.signature,
                migrate = False
)



db.define_table('case_master',
                Field('case_number'),
                Field('member_id', 'reference client', ondelete='NO ACTION'),
                Field('description','text'),
                Field('date_assigned', 'date'),
                Field('date_closed','date'),
                Field('dead_file_box_number'),
                Field('assigned_to', 'reference auth_user', ondelete='NO ACTION'),
               
#                auth.signature,
                
                migrate = False
 )

db.define_table('case_action',
                Field('case_id', 'reference case_master'),
                Field('action_id', 'reference case_action_master'),
                Field('date_performed', 'date'),
                Field('remarks', 'text'),
 #               auth.signature,
                migrate = False
 )

db2.define_table('member',
                 Field('id_no','integer'),
                 Field('name', 'string','length=21'),
                 Field('first_name', 'string', 'length=21'),
                 Field('minst', 'string', 'length=7'),
                 Field('address','string', 'length=35'),
                 Field('zip','string', 'length=10'),
                 Field('phone','string', 'length=13'),
                 Field('email','string', 'length= 50'),
                 Field('stat','string','length=3'),
                 primarykey = ['id_no'],
                 migrate = False)
