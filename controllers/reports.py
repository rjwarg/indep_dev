# coding: utf8
# try something like
import html, datetime
from gluon.storage import Storage

def index(): return dict(message="hello from reports.py")

def cases_pdf():
    
    db_rows = db(db.case_master.assigned_to == auth.user.id).select()
#    db_rows = db(db.case_master).select()
    response.title = "Indep Counsel's Cases"

    rows = []

    from gluon.contrib.pyfpdf import FPDF, HTMLMixin

        # define our FPDF class (move to modules if it is reused  frequently)
    class MyFPDF(FPDF, HTMLMixin):
            def header(self):
                self.set_font('Arial','B',15)
                self.cell(0,10, response.title ,1,0,'C')
                self.ln(20)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial','I',8)
                txt = 'Page %s of %s' % (self.page_no(), self.alias_nb_pages())
                self.cell(0,10,txt,0,0,'C')
                    
    pdf=MyFPDF()
    pdf.add_page()
    pdf.set_font('arial')

    # change the font
    pdf.set_font('helvetica', size=9)
    pdf.set_fill_color(200)
    pdf.cell(25,5,'Case Number',1, fill=True)
    pdf.cell(35,5,'Member Name',1, fill=True)
    pdf.cell(25,5,'Date Assigned',1, fill=True)
    pdf.cell(95,5,'Description',border=1, fill=True )
    pdf.ln(5)
    pdf.ln(5)
    pdf.set_fill_color(255,200,200)
    filler = False
    for row in db_rows:
            pdf.cell(25,5,row.case_number,1, fill=filler)

            pdf.cell(35,5,row.member_id.last_name,1,fill=filler)
            pdf.cell(25,5,str(row.date_assigned),1,fill=filler)
            pdf.multi_cell(95,5,row.description,border=1,fill=filler )
            pdf.ln(5)
            filler = not filler

       
    response.headers['Content-Type']='application/pdf'
    return pdf.output(dest='S')

# list the adverse witnesses

def adv_wit_list_B():
#    rows = db.executesql("select A.* , B.username , C.case_number "+
#                         "from adverse_witness A  "+
#                         "join auth_user B on b.id = a.assigned_to "+
#                         "join case_master C on C.id = a.case_id;")
    rows = db(db.adverse_witness.assigned_to == auth.user.id).select(db.adverse_witness.ALL)
    cases = []
    fieldnames = ['case_number','last_name', 'first_name', 'member_id', 'remarks','counsel', 'case_row_id']
#    return dict(rows = rows,fieldnames = fieldnames)
    for row in rows:
        cs = Storage()
        case= Storage( {'member_id': row.member_id, 
               'last_name': row.last_name, 
               'first_name': row.first_name, 
               'remarks': row.remarks,
               'counsel': row.assigned_to.username,
               'case_number': row.case_id.case_number,
               'case_row_id': row.case_id
               })
        cases.append(case)
    return response.render("reports/adv_wit_list.html",    dict(rows = cases, fieldnames = fieldnames ))
#    return dict(rows = cases, fieldnames = fieldnames )


def adv_wit_list():
    rows = db.executesql("select A.* , B.username , C.case_number, C.assigned_to "+
                         "from adv_wit A  "+
                         "join case_master C on C.id = a.case_id "+
                         "join auth_user B on b.id = C.assigned_to "+
                         "where C.assigned_to = " + str( auth.user.id) +
                         " order by last_name;" )
                         
#    rows = db(db.adv_wit).select()
    cases = []
    fieldnames = ['case_number','last_name', 'first_name', 'member_id', 'remarks','counsel', 'case_row_id']
#    return dict(rows = rows,fieldnames = fieldnames)
    for row in rows:
        cs = Storage()
       
        case= Storage( {'member_id': row.member_id, 
               'last_name': row.last_name, 
               'first_name': row.first_name, 
               'remarks': row.remarks,
               'counsel': row.username,
               'case_number': row.case_number,
               'case_row_id': row.case_id,
               'assigned_to': row.assigned_to,
               'user_type': auth.user.id
               })
        cases.append(case)
    return response.render("reports/adv_wit_list.html",    dict(rows = cases, fieldnames = fieldnames ))
#    return dict(rows = cases, fieldnames = fieldnames )
def case_rpt():
     u = auth.user
     filename = ""
     title = "Case List"
     report_type = request.args(0)
     if request.args(0) == "Active":
        rows = db((db.case_master.date_closed == None) & (db.case_master.assigned_to == u.id)).select(orderby=~db.case_master.case_number)
        filename = "active_cases.csv"
        title = "Active Case List"
     elif request.args(0) == 'Closed':
        rows = db((db.case_master.date_closed != None) & (db.case_master.assigned_to == u.id)).select(orderby=~db.case_master.case_number)      
        filename = "closed_cases.csv"
        title = "Closed Case List"
     elif request.args(0) == 'Client':
        rows = db(db.case_master.assigned_to == u.id).select(orderby=db.case_master.member_id)
        title = "Case List by Client"
        filename = "client_cases.csv"        
     else:
        rows = db(db.case_master and db.case_master.assigned_to == u.id).select(orderby=~db.case_master.case_number)
        filename = "all_cases.csv"
        report_type = "All"
     
     fieldnames = ['case_number','member_id', 'member_name','description', 
                   'date_assigned', 'date_closed', 'dead_file_box_number','counsel', 'case_row_id']
#    return dict(rows = rows,fieldnames = fieldnames)
     cases = []
     for row in rows:
        cs = Storage()
        case= Storage( {'member_id': row.member_id, 
               'member_name': row.member_id.last_name + ', ' + row.member_id.first_name,         
               'date_assigned': row.date_assigned, 
               'date_closed': row.date_closed, 
               'description': row.description,
               'dead_file_box_number': row.dead_file_box_number,
               'counsel': row.assigned_to.username,
               'case_number': row.case_number,
               'case_row_id': row.id
               })
        cases.append(case)
     case_type ="cases.csv"
     if request.args(0) == "Client":
         cases = sorted(cases, key = lambda case: case.member_name)
     return dict(rows = cases, fieldnames = fieldnames, filename = filename, title = title, report_type = report_type)


def action_display():
    u = auth.user
    args = request.args
    from_date =args[0]
    to_date = args[1]
    t = type(from_date)
    fd = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
    td = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
    tt = type(fd)
    query = db.case_action.date_performed >= fd
    query &= db.case_action.date_performed <= td
    query &= (db.case_action.case_id == db.case_master.id) 
    query &= (db.case_master.assigned_to == u.id)
    rows =  db(query).select(db.case_action.ALL)# orderby=db.case_action.case_id)
    filename = "actions.csv"
#    rows = []
#    for r in rows_a:
#        if r.case_id.assigned_to == u.id:
#            rows.append(r)
            
    response.title = "Indep Counsel"
    return locals()

def action_rpt():
    u = auth.user
    if  u is None:
        response.flash = 'Not signed in'
        return locals()
    rows = db(db.case_action.id ).select()
    to_date = datetime.date.today() 
    from_date = to_date - datetime.timedelta(30)
    form = FORM('From Date:', INPUT(_name='from_date', _class='date', widget=SQLFORM.widgets.date.widget, value=from_date, requires=IS_DATE()),
                'To Date:', INPUT( _name='to_date', _class='date', widget=SQLFORM.widgets.date.widget,value = to_date, requires=IS_DATE()),
                INPUT(_type ='submit'))  
    if form.accepts(request,session):
        response.flash = 'form accepted '
        redirect(URL('action_display', args=(request.vars.from_date, request.vars.to_date)))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
        
    response.title = "Indep Counsel"
    return locals()


def case_rtf():

    import gluon.contrib.pyrtf as q
    doc=q.Document()
    ss= doc.StyleSheet
    section=q.Section()
    doc.Sections.append(section)
    para_props = q.ParagraphPS(tabs = [q.TabPS(width= q.TabPS.DEFAULT_WIDTH *3),
                                       q.TabPS(width= q.TabPS.DEFAULT_WIDTH *6),
                                       q.TabPS(width=q.TabPS.DEFAULT_WIDTH *8)])
    p = q.Paragraph(ss.ParagraphStyles.Heading1, para_props)
    p.append('Independent Counsel Case Tracking')
    section.append(p)
    rows = db().select(db.case_master.ALL)
   
    p = q.Paragraph(ss.ParagraphStyles.Heading2, para_props)
    p.append("Case Number", q.TAB, "Member Name", q.TAB, "Assigned Date")
    section.append(p)   
    for row in rows:
        p = q.Paragraph(ss.ParagraphStyles.Normal, para_props)
        p.append(row.case_number,q.TAB, row.member_id.last_name, q.TAB, str(row.date_assigned) )
        section.append(p)
    response.headers['Content-Type']='text/rtf'
    return q.dumps(doc)
