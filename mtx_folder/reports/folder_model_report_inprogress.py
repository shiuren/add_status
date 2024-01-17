# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FolderModel(models.TransientModel):
    _name = 'folder.report.inprogress'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', required=True, string="Client")
    adress = fields.Char(string="Adresse", readonly=True, related='partner_id.street' )
    folder_ids = fields.Many2many('folder.model', string="Dossier", compute="_compute_folder_line_inprogress")
    date_from = fields.Date(string="Début")
    date_end = fields.Date(string="Fin")

    @api.depends('date_from','date_end','partner_id')
    def _compute_folder_line_inprogress(self):
        for rec in self:
            folder_ids = False
            if rec.date_from and rec.date_end and self.partner_id:
                domain = [('partner_id', '=', self.partner_id.id),
                          ('date', '>=', self.date_from),
                          ('date', '<=', self.date_end),
                          ('state','=','in_progress')]
                folder_ids = self.env['folder.model'].search(domain)
            rec.folder_ids = folder_ids


    def do_report_folder_inprogress(self):
        return self.env.ref('mtx_folder.print_folder_report_inprogress_pdf').report_action(self)
    

    def get_report_folder_progress(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rapport en cours',
            'view_mode': 'list,form',
            'res_model': 'folder.model',
            'domain': [('partner_id', '=', self.partner_id.id),
                       ('date', '>=', self.date_from),
                       ('date', '<=', self.date_end),
                       ('state','=','in_progress')],
            'context': "{'create': False}"
        }
    