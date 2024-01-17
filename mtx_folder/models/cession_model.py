# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
import re

class CessionModel(models.Model):
   _name = 'cession.model'
   _description = 'Cession Model'
   _rec_name = "cession_number"

   name = fields.Char(string='Nom')
   company_id = fields.Many2one('res.company', 'Company', index=True)
   currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id_')
   
   @api.depends('company_id')
   def _compute_currency_id_(self):
      main_company = self.env['res.company']._get_main_company()
      for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id


   active = fields.Boolean(default=True)
   type_freight = fields.Selection(
      string="Type de fret",
      selection=[('air','Aérien'),('maritime','Maritime')],
      required=True,
      default=""
   )
   
   title_type_freight = fields.Char(readonly=True, store=True, force_save=True, compute="_compute_title_freight")
   
   # On change type freight
   @api.depends('type_freight')
   def _compute_title_freight(self):
      for record in self:
         if record.type_freight == 'air':
            record.title_type_freight = "TYPE AÉRIEN"
         elif record.type_freight == "maritime":
            record.title_type_freight = "TYPE MARITIME"
         else:
            record.title_type_freight = "TYPE DE FRET"
   
   
   freight_mode = fields.Selection(
      string="Mode",
      selection=[('import','Import'),('export','Export')])
   invoice_number = fields.Char(string="Numéro de facture")
   cession_number = fields.Char(string="Numéro du Cession", required=True)
   date = fields.Date(string="Date",default=lambda self: datetime.today())
   responsible = fields.Many2one('res.users', required=True, string='Responsable', default=lambda self: self.env.user.id)
   partner_id = fields.Many2one('res.partner', required=True, string="Client")
   ref_ot_client = fields.Char(string="Réf OT Client", required=True)

   

   eta_date = fields.Date(string="ETA")
   date_dau = fields.Date(string="Date DAU")
   date_filing_declaration = fields.Date(string="Dépot déclartion")
   dau_number = fields.Char(string="Numéro DAU")
   end_of_shipping_franchise = fields.Date(string="Fin franchise magasinage")
   end_of_demurrage_exemption = fields.Date(string="Fin franchise surestarie")
   num_blta = fields.Char(string="Num BL/LTA")
   num_hwb = fields.Char(string="Numero HWB")
   air_consolidation = fields.Char(string="Groupage Aérien (GA)")
   submission = fields.Char(string="Soumission")
   submission_date = fields.Date(string="Date reg soumission")
   circuit_cs = fields.Char(string="Circuit C/S")
   payment_order = fields.Char(string="Ordre de virement")
   payment_date = fields.Date(string="Date de virement")
   num_bsc = fields.Char(string="Bsc Numero")
   midac_authorization = fields.Char(string="Midac autorisation")
   delivery_date = fields.Date(string="Date de livraison")
   date_sending_doc_tmm = fields.Date(string="Date d'envoie Doc TMM")
   delivery_place = fields.Char(string="Lieu de livraison")
   provision = fields.Float(string="Provisions")
   provision_ot = fields.Float(string="Provisions OT")
   check_number_provision = fields.Char(string="Numero Chèque provision")
   agio = fields.Char(string="Agio")
   num_dau_mb = fields.Char(string="Numéro DAU/MB")
   circuit_imb = fields.Char(string="Circuit IMB")
   due_date = fields.Date(string="Date d'échéance")
   submission_date_depot = fields.Date(string="Date de depôt soumission")
   submission_date_depot_end = fields.Date(string="Date de fin", compute="_compute_end_date_submission")

   is_fefteen_day = fields.Boolean(string="15ème jours")
   days_left = fields.Integer(string="Nombre de jours restantes", compute="_compute_days_left")
   is_fifteen = fields.Boolean(compute="_compute_is_fifteen", store=True)

   @api.depends('submission_date_depot')
   def _compute_end_date_submission(self):
      for record in self:
         if record.submission_date_depot:
               start_date_str = record.submission_date_depot.strftime('%Y-%m-%d')
               start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
               end_date = start_date + relativedelta(days=+60)
               record.submission_date_depot_end = end_date
         else:
               record.submission_date_depot_end = False

   @api.depends('submission_date_depot')
   def _compute_days_left(self):
      for record in self:
         if record.submission_date_depot and record.submission_date_depot_end:
               today = datetime.now().date()
               days_left = (record.submission_date_depot_end - today).days
               record.days_left = abs(days_left - 60)
         else:
               record.days_left = 0

   @api.depends('days_left')
   def _compute_is_fifteen(self):
      for record in self:
         if record.days_left in  [60,45,30,15]:
               record.is_fifteen = True
         else:
               record.is_fifteen = False
           
           
           
   state = fields.Selection(
      selection=[('draft','Brouillon'),('in_progress','En cours'),('complete','Complet'),('terminated','Résilié')],
      default="draft"
   )
   tc_ids = fields.Many2many('tc.model')
   # tc = fields.Char(string="TC")
   missing_doc = fields.Html(string="Document manquants")
   goods = fields.Html(string="Marchandises")
   observations = fields.Html(string="Observations")
   is_complete = fields.Boolean(string="Doc complet", readonly=False, force_save=True, store=True)
   doc_line_ids = fields.One2many('doc.cession.line','doc_cession_line_id',  string="Déclarants")
   attachement_line_ids = fields.One2many('attachement.cession.lines','attachement_cession_line_id',  string="Autres Pièces Jointes")

   @api.onchange('doc_line_ids')
   def _onchange_complete(self):
      for rec in self:
         if rec.doc_line_ids:
               rec.is_complete = True
               rec.state = 'complete'
         else:
               rec.is_complete = False
               rec.state = 'draft'

   historical = fields.Html(string="Historiques")

   def action_confirm(self):
      for rec in self:
         if rec.state == 'in_progress':
            raise exceptions.ValidationError("Le dossier se trouvant déjà à l'état En cours.")
         rec.state = 'in_progress'


   def action_cancel(self):
      for rec in self:
         if rec.state == 'terminated':
            raise exceptions.ValidationError("Le dossier se trouvant déjà à l'état Résilié.")
         rec.state = 'terminated'
   
   def unlink(self):
        for rec in self:
           if rec.state != 'draft':
              raise exceptions.ValidationError("Impossible de supprimer un enregistrement. Veuillez l'archiver au lieu de le supprimer.")
        return super(CessionModel, self).unlink()
   
   case_freight = fields.Char(string="Dossier Frêt")
   case_franchise = fields.Char(string="Dossier Franchise (F)")
   case_transport = fields.Char(string="Dossier transport (TR)")

   import_export_invoice_doc = fields.Binary(string='Facture Import Export')
   packing_doc = fields.Binary(string="Colisage")
   bsc_doc = fields.Binary(string="BSC")
   bl_doc = fields.Binary(string="BL")
   ot_doc = fields.Binary(string="OT")
   domiciliation_doc = fields.Binary(string="Domiciliation")
   autorisation_doc = fields.Binary(string="Autorisation")
   midac_doc = fields.Binary(string="Midac")
   doc_datas = fields.Binary(string='Database Data', attachment=False)
   @api.depends('doc_datas')
   def _compute_doc(self):
      for rec in self:
         rec.import_export_invoice_doc = base64.b64encode(rec.import_export_invoice_doc or b'')
         rec.packing_doc = base64.b64encode(rec.packing_doc or b'')
         rec.bsc_doc = base64.b64encode(rec.bsc_doc or b'')
         rec.bl_doc = base64.b64encode(rec.bl_doc or b'')
         rec.ot_doc = base64.b64encode(rec.ot_doc or b'')
         rec.domiciliation_doc = base64.b64encode(rec.domiciliation_doc or b'')
         rec.autorisation_doc = base64.b64encode(rec.autorisation_doc or b'')
         rec.midac_doc = base64.b64encode(rec.midac_doc or b'')
      return
   
   etd_date = fields.Date(string="ETD")
   potting_date = fields.Date(string="Date d'empotage")
   potting_place = fields.Char(string="Lieu d'empotage")
   destination = fields.Char(string='Destination')
   n_plomb = fields.Char(string="Numéro plomb")

   type_m_se = fields.Selection(
       string="Type m/se",
       selection=[('container','Conteneur'),('grouping','Groupage')]
   )
   container_twenty = fields.Char(string="Conteneur 20")
   container_fourty = fields.Char(string="Conteneur 40")
   container_total = fields.Integer(string="Total Conteneur", store=True, force_save=True, compute="_compute_container_total")

   @api.depends('container_twenty','container_fourty')
   def _compute_container_total(self):
       for record in self:
            total = 0
            if record.container_twenty:
                # Utilise une expression régulière pour extraire les chiffres de la chaîne
                numbers = re.findall(r'\d+', record.container_twenty)
                # Somme des chiffres extraits
                total += sum(map(int, numbers))
            if record.container_fourty:
                numbers = re.findall(r'\d+', record.container_fourty)
                total += sum(map(int, numbers))
            record.container_total = total
   
   ship = fields.Char(string="Navire")

   weight = fields.Float(string="Poids")
   volume = fields.Float(string="Volume")

   date_manifest = fields.Date(string="Date Manifeste")
   effective_payment_date = fields.Date(string="Date de paiement effective")
   collection_date = fields.Date(string="Date d'enlèvement")
   folder_reference = fields.Char(string="Référence du dossier")

   check_number = fields.Char(string="N° Chèques")
   payment_info = fields.Html(string="Informations de paiement")

   folder_model_id = fields.Many2one('folder.model', string="Dossier")
           


class AttachementCessioinLines(models.Model):
      _name = 'attachement.cession.lines'
      _description = 'Pièces Jointes'

      attachement_name = fields.Char(string="Nom")
      attachement_type = fields.Selection(
         string="Type",
         selection=[('import_export_invoice','Facture Import Export'),('packing','Colisage'),('bsc','BSC'),('bl','BL'),('ot','OT'),('domoiciliation','Domiciliation'),('autorisation','Autorisation'),('midac','Midac')],
         default="import_export_invoice")
      attachement = fields.Binary(string='Pièces jointes')
      attachement_datas = fields.Binary(string='Database Data', attachment=False)
      attachement_cession_line_id = fields.Many2one('cession.model')

      @api.depends('attachement_datas')
      def _compute_doc(self):
         for rec in self:
               rec.doc = base64.b64encode(rec.doc or b'')
         return
      

class DocumentCessionLinei(models.Model):
    _name = 'doc.cession.line'
    _description = 'Ligne de document'

    doc = fields.Binary(string='Document')
    doc_datas = fields.Binary(string='Database Data', attachment=False)
    doc_cession_line_id = fields.Many2one('cession.model')
    

    @api.depends('doc_datas')
    def _compute_doc(self):
        for rec in self:
            rec.doc = base64.b64encode(rec.doc or b'')
        return