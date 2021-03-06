# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
from datetime import date
import time

# global client record
global_client = ""

 
@auth.requires_membership('CCPOA Information Technology')
def index():
    u = auth.user
   
   
    response.flash = "who is logged in? " + u.first_name + " " + u.last_name + " " +str( u.id)
    if request.args(0) == None:
        rows = db((db.case_master.date_closed == None) & (db.case_master.assigned_to == u.id)).select(orderby=~db.case_master.case_number)
        case_type = "Active"
    elif request.args(0) == 'C':
        rows = db((db.case_master.date_closed != None) & (db.case_master.assigned_to == u.id)).select(orderby=~db.case_master.case_number)      
        case_type = "Closed"
    else:
        rows = db(db.case_master and db.case_master.assigned_to == u.id).select(orderby=~db.case_master.case_number)
        case_type = "All"
    return locals()


@auth.requires_login()
def get_members():
    members_list = db2(db2.member.name.startswith(request.args[0])).select()
    return locals()

@auth.requires_login()
def show_ajax():
    if request.vars.id != '':
        if request.vars.selection == "adv_wit":
                response.flash = "Add Adverse Witness"
                redirect(URL('edit_witness', args=(request.vars.id, 'new' )))
        if request.vars.selection == "case":
               response.flash = "Now create a case for this person"
               redirect(URL('edit_case', args=(request.vars.id, 'new')))
    else:
        response.flash = "No client was selected. Please try again or go back. " + request.vars.selection
        
    if request.vars.path_option:
        path_option = request.vars.path_option
    elif request.vars.selection:
        path_option = request.vars.selection
    if path_option == 'adv_wit' :
        button_label = "Add Witness"
    else:
        path_option = 'case'
        button_label = "Create Case"
    return locals()

def edit_witness_2():
    '''
    doc test for edit_witness
    >>> from gluon.globals import Request
    >>> request = Request()
    >>> request.args = ('57921', "new")
    >>> print request.args
    ('57921', 'new')
    >>> edit_witness_2()
    {retval = 'new'}
    
    '''
    request = Request()
    retval = request.args(1)
    return locals()

def edit_witness():
    
    adv_wit_record_id = request.args(1)
    if adv_wit_record_id == 'new':
        form = SQLFORM(db.adv_wit)
        form.vars.member_id = request.args(0)
#        case_id_name = db.case_master(request.args(0)).case_number
        form.vars.case_id = session.case_id
        member = db2.member(request.args(0))
        form.vars.last_name = member.name
        form.vars.first_name = member.first_name
#        form.vars.assigned_to = 4
       
        hold = [request.args(0),  "new"]
    else:
        witness = db.adv_wit(adv_wit_record_id)
        case_id_name = db.case_master(witness.case_id).case_number
#        case_id_name = witness.case_id.case_number 
        form = SQLFORM(db.adv_wit, witness, deletable=True)
        
        hold = [request.args(0), witness.id, "existing"]
# add a cancel button
    form.add_button('Cancel', "javascript:void(history.go(-1))")
    if form.process(session=None, formname='indep').accepted:
        response.flash = 'form accepted'
        if request.env.http_referrer:
            redirect(request.env.http_referrer)
        else:
            redirect(URL('edit_case', args=(session.case_id)))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill in the form'
    
    return locals()

def ttest():
    ''' 
    doctest for ttst()
    >>> name = 'richard'
    >>> ttest()
    {'name': 'richard'}
    '''   
    name = 'richard'
    return dict(name=name)

def edit_action():
    db.case_action.action_id.requires = IS_IN_DB(db,'case_action_master.id', '%(action_name)s')
    action_record_id = request.args(1)
    if action_record_id == '0':
        form = SQLFORM(db.case_action)
        form.vars.case_id = request.args(0)
        case_id_name = db.case_master(request.args(0)).case_number
        form.vars.action_id = request.args(1)
        form.vars.date_performed = date.today()
        hold = [request.args(0),  "new", case_id_name]
    else:
        action = db.case_action(action_record_id)
#        case_id_name = db.case_master(action.case_id).case_number
        case_id_name = action.case_id.case_number 
        form = SQLFORM(db.case_action, action, deletable = True)
        
        hold = [request.args(0), action.id, "existing"]
    form.add_button('Cancel', "javascript:void(history.go(-1))")
    if form.process(session=None, formname='indep').accepted:
        response.flash = 'form accepted'
        if request.env.http_referrer:
            redirect(request.env.http_referrer)
        else:
            redirect(URL('edit_case', args=(request.args(0))))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill in the form'
    
    client = db.mclient(db.case_master(request.args(0)).member_id)
    client_name = client.first_name + " " + client.last_name
    return locals()

def insert_client(member_id):
    # is there already a client record for this member?
    client = db(db.mclient.member_id == member_id).select().first()
    if client == None:
        # get the member data
        member = db2(db2.member.id_no == member_id).select().first()
        db.mclient.insert(member_id = member_id, 
                         last_name = member.name, 
                         first_name = member.first_name,
                         minst = member.minst,
                         address = member.address,
                         zip = member.zip,
                         stat = member.stat)
        client = db(db.mclient.member_id == member_id).select().first()
    return client


def edit_case():
    hold = 0
    rq = ""
    testing = "testing"
    case_number = request.args(1)
    if case_number == 'new':
        case_number = new_case_number()
        # create a new client record from the member master table
        form = SQLFORM(db.case_master)
        form.vars.case_number = case_number
        form.vars.member_id = request.args(0)
        form.vars.date_assigned = date.today()
        form.vars.assigned_to = auth.user.id
#        client = db.client( request.args(0))
#        client = db(db.client.member_id == request.args(0)).select().first()
        client = insert_client(request.args(0))
        hold = 0
       
        # insert a new case_action record for the assignment
  
    else:
        rq = request
        case_id = request.args(0)
        case = db.case_master(case_id)
        client = db.mclient(case.member_id)
        form = SQLFORM(db.case_master, case)
        # get list of actions
        actions = db(db.case_action.case_id == case).select()
        witnesses = db(db.adv_wit.case_id == case).select()
#        hold = case.case_number
        hold = case.id
        session.case_id = case.id
    form.add_button('Cancel', "javascript:void(history.go(-1))")    
    if form.process(session=None, formname='indep').accepted:
        response.flash = 'form accepted'
        # if this is a new record then insert a new case_action
        if hold ==0:
              db.case_action.insert(case_id = form.vars.id, action_id = 1, date_performed = form.vars.date_assigned)
        redirect(URL('index'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill in the form'
        
    
        
    return locals()


def name_selector():
    
        
    if not request.vars.last_name: return ''
    
    pattern = request.vars.last_name.upper() + '%' 
    query = db2.member.name.like(pattern)
    if request.vars.first_name:
         pattern = request.vars.first_name.upper() + '%' 
         query &= db2.member.first_name.like(pattern)
            
    if request.vars.minst:
         pattern = request.vars.minst.upper() + '%' 
         query &= db2.member.minst.like(pattern)
     
    selected = [{'last_name':row.name, 'first_name':row.first_name, 'minst':row.minst, 'member_id':str(row.id_no)}for row in
               db2(query).select(orderby=db2.member.name | db2.member.first_name, limitby=(0,25))]
#    return "testing away"
    #db(db.member.name.like(pattern)).select(orderby=db.member.name, limitby=(0, 15))]
    return ''.join([DIV(k['last_name']+', '+k['first_name'] +', '+k['minst'],
                       _onclick="set_text('" +k['last_name']+"','"+k['first_name']+"','"+k['minst']+"','"+k['member_id']+"')",
                       _onmouseover="this.style.backgroundColor='yellow'",
                       _onmouseout="this.style.backgroundColor='white'"
                       ).xml() for k in selected])


def orig_name_selector():
    
        
    if not request.vars.name: return ''
    
    pattern = request.vars.name.upper() + '%' 
    query = db2.member.name.like(pattern)
    if request.vars.first_name:
         pattern = request.vars.first_name.upper() + '%' 
         query &= db2.member.first_name.like(pattern)
            
    if request.vars.minst:
         pattern = request.vars.minst.upper() + '%' 
         query &= db2.member.minst.like(pattern)
     
    selected = [{'last_name':row.name, 'first_name':row.first_name, 'minst':row.minst, 'id':str(row.id_no)}for row in
               db2(query).select(orderby=db2.member.name | db2.member.first_name, limitby=(0,25))]
#    return "testing away"
    #db(db.member.name.like(pattern)).select(orderby=db.member.name, limitby=(0, 15))]
    return ''.join([DIV(k['last_name']+', '+k['first_name'] +', '+k['minst'],
                       _onclick="set_text('" +k['last_name']+"','"+k['first_name']+"','"+k['minst']+"','"+k['id']+"')",
                       _onmouseover="this.style.backgroundColor='yellow'",
                       _onmouseout="this.style.backgroundColor='white'"
                       ).xml() for k in selected])

def dummy():
    vals = "this is a test entry"
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
def new_case_number():
    
 
    suffix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    date_part = date.today().strftime("%y%m%d")
    # howmany cases start with this date?
    count = db(db.case_master.case_number.like(date_part +'%')).count()
    return date_part + suffix[count:count+1]
