# Premiérement dans cette exercice on me demande de créer une contrainte; c'est à dire q'à chaque enregistrement d'un nom, il doit être unique plus présisement qu'on ne peut utiliser le même nom
### Voici les deux champs en question la valeur du champ "folder_number_uniq" doit être unique et de même pour num_blta

_sql_constraints = [
        ('folder_number_uniq', 'unique (folder_number)', 'The name of the account must be unique per company !')
    ]

   _sql_constraints = [
        ('num_blta', 'unique (num_blta)', 'The blta of the account must be unique per company !')
    ]

# Deuxiemement ajouter un boutton qui permettrait de faire un retour à une étape précedente
### voici les étapes sur le champ state:

   state = fields.Selection(
      selection=[('draft','Brouillon'),('in_progress','En cours'),('complete','Complet'),('terminated','Résilié')],
      default="draft"
   )
   
### Voici l'étape de retour , interprétation : si le statut d'un projet, ou d'une teste est différent de draft, alors le statut est égal à draft. On lecture simple l'étape d'un projet est en mode brouillon (draft = draft; attention ceci n'est q'une lécture global et simple)
   def action_brouillon(self):
      for rec in self:
         if rec.state != 'draft':
            rec.state = 'draft'

# Troisième étape afficher l'action dans la vue xml; mais pour plus de clarté afficher le boutton si nécessaire pendant une étape
### Après confirmation d'une étape le boutton apparaît , si non dans le sens contraîre retour en arrière

        <header>
          <button string="Confirmer" confirm="Vous voulez vraiment confirmer?" name="action_confirm" type="object" class="bg_blue_btn text-light" attrs="{'invisible': ['|',('state', '=',                           'terminated'),('state','=','in_progress')]}"/>
          <button string="Annuler" confirm="Vous voulez vraiment annuler?" name="action_cancel" type="object" class="bg-light text-danger" attrs="{'invisible': ['|',('state', '=', 'terminated'),                    ('state','=','in_progress')]}"/>
          <button string="brouillon" confirm="Vous voulez vraiment mettre en brouillon?" name="action_brouillon" type="object" class="bg_blue_btn text-light" attrs="{'invisible': [('state', '=', '                  draft')]}"/>
          <field name="state" widget="statusbar" statusbar_visible="draft,in_progress,complete,terminated" />
        </header>
