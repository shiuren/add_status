# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TcModel(models.Model):
    _name = 'tc.model'
    _description = 'TC'

    name = fields.Char(string='Nom')
    color = fields.Integer(string='Couleur')