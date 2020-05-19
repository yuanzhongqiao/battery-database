# Generated by Django 2.2.11 on 2020-05-17 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.CharField(blank=True, max_length=100, null=True)),
                ('proprietary', models.BooleanField(blank=True, default=False)),
                ('proprietary_name', models.BooleanField(blank=True, default=False)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('description_name', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CoatingLot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coating', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='cell_database.Coating')),
            ],
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.CharField(blank=True, max_length=1000, null=True)),
                ('smiles', models.CharField(blank=True, max_length=1000, null=True)),
                ('smiles_name', models.BooleanField(blank=True, default=False)),
                ('proprietary', models.BooleanField(blank=True, default=False)),
                ('proprietary_name', models.BooleanField(blank=True, default=False)),
                ('composite_type', models.CharField(blank=True, choices=[('el', 'electrolyte'), ('ed', 'electrode'), ('se', 'separator')], max_length=2)),
                ('composite_type_name', models.BooleanField(blank=True, default=False)),
                ('component_type', models.CharField(blank=True, choices=[('sa', 'salt'), ('ad', 'additive'), ('so', 'solvent'), ('am', 'active_material'), ('co', 'conductive_additive'), ('bi', 'binder'), ('se', 'separator_material')], max_length=2)),
                ('component_type_name', models.BooleanField(blank=True, default=False)),
                ('coating_lot_name', models.BooleanField(blank=True, default=False)),
                ('particle_size', models.FloatField(blank=True, help_text='micrometers', null=True)),
                ('particle_size_name', models.BooleanField(blank=True, default=False)),
                ('single_crystal', models.CharField(blank=True, choices=[('sc', 'Single'), ('po', 'Poly'), ('mx', 'Mixed')], max_length=2, null=True)),
                ('single_crystal_name', models.BooleanField(blank=True, default=False)),
                ('turbostratic_misalignment', models.FloatField(blank=True, help_text='percent', null=True)),
                ('turbostratic_misalignment_name', models.BooleanField(blank=True, default=False)),
                ('preparation_temperature', models.FloatField(blank=True, help_text='celsius', null=True)),
                ('preparation_temperature_name', models.BooleanField(blank=True, default=False)),
                ('natural', models.BooleanField(blank=True, null=True)),
                ('natural_name', models.BooleanField(blank=True, default=False)),
                ('coating_lot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.CoatingLot')),
            ],
        ),
        migrations.CreateModel(
            name='ComponentLot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='cell_database.Component')),
            ],
        ),
        migrations.CreateModel(
            name='Composite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proprietary', models.BooleanField(blank=True, default=False)),
                ('proprietary_name', models.BooleanField(blank=True, default=False)),
                ('composite_type', models.CharField(blank=True, choices=[('el', 'electrolyte'), ('ca', 'cathode'), ('an', 'anode'), ('se', 'separator')], max_length=2)),
                ('composite_type_name', models.BooleanField(blank=True, default=False)),
                ('notes', models.CharField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompositeLot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('composite', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='cell_database.Composite')),
            ],
        ),
        migrations.CreateModel(
            name='DryCell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.CharField(blank=True, max_length=1000, null=True)),
                ('proprietary', models.BooleanField(blank=True, default=False)),
                ('proprietary_name', models.BooleanField(blank=True, default=False)),
                ('geometry_name', models.BooleanField(blank=True, default=False)),
                ('cathode_name', models.BooleanField(blank=True, default=False)),
                ('anode_name', models.BooleanField(blank=True, default=False)),
                ('separator_name', models.BooleanField(blank=True, default=False)),
                ('anode', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='anode', to='cell_database.CompositeLot')),
            ],
        ),
        migrations.CreateModel(
            name='DryCellGeometry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geometry_category', models.CharField(blank=True, choices=[('po', 'pouch'), ('cy', 'cylinder'), ('st', 'stack'), ('co', 'coin')], max_length=2)),
                ('geometry_category_name', models.BooleanField(blank=True, default=False)),
                ('width', models.FloatField(blank=True, help_text='Millimeters (mm)', null=True)),
                ('width_name', models.BooleanField(blank=True, default=False)),
                ('length', models.FloatField(blank=True, help_text='Millimeters (mm)', null=True)),
                ('length_name', models.BooleanField(blank=True, default=False)),
                ('thickness', models.FloatField(blank=True, help_text='Millimeters (mm)', null=True)),
                ('thickness_name', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DryCellLot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dry_cell', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='cell_database.DryCell')),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeGeometry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loading', models.FloatField(blank=True, help_text='milligrams per squared centimeters', null=True)),
                ('loading_name', models.BooleanField(blank=True, default=False)),
                ('density', models.FloatField(blank=True, help_text='grams per cubic centimeters', null=True)),
                ('density_name', models.BooleanField(blank=True, default=False)),
                ('thickness', models.FloatField(blank=True, help_text='micrometers', null=True)),
                ('thickness_name', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeMaterialStochiometry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atom', models.CharField(blank=True, choices=[('Li', 'LITHIUM'), ('O', 'OXIGEN'), ('C', 'CARBON'), ('Ni', 'NICKEL'), ('Mn', 'MANGANESE'), ('Co', 'COBALT'), ('Mg', 'MAGNESIUM'), ('Al', 'ALUMINUM'), ('Fe', 'IRON'), ('P', 'PHOSPHORUS'), ('Ti', 'TITANIUM'), ('S', 'SULFUR'), ('Na', 'SODIUM'), ('F', 'FLUORINE'), ('Cl', 'CHLORINE'), ('Cu', 'COPPER'), ('Zn', 'ZINC'), ('Mo', 'MOLYBDENUM'), ('Nb', 'NIOBIUM'), ('Si', 'SILICON'), ('Pt', 'PLATINUM')], max_length=3)),
                ('stochiometry', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LotInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.CharField(blank=True, max_length=100, null=True)),
                ('creator', models.CharField(blank=True, max_length=100, null=True)),
                ('creator_name', models.BooleanField(blank=True, default=False)),
                ('date', models.DateField(blank=True, help_text='YYYY-MM-DD', null=True)),
                ('date_name', models.BooleanField(blank=True, default=False)),
                ('vendor', models.CharField(blank=True, max_length=300, null=True)),
                ('vendor_name', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SeparatorGeometry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thickness', models.FloatField(blank=True, help_text='millimeters', null=True)),
                ('thickness_name', models.BooleanField(blank=True, default=False)),
                ('width', models.FloatField(blank=True, help_text='millimeters', null=True)),
                ('width_name', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WetCell',
            fields=[
                ('cell_id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('dry_cell', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.DryCellLot')),
                ('electrolyte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.CompositeLot')),
            ],
        ),
        migrations.CreateModel(
            name='RatioComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ratio', models.FloatField(blank=True, null=True)),
                ('component_lot', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='cell_database.ComponentLot')),
            ],
        ),
        migrations.AddField(
            model_name='drycelllot',
            name='lot_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.LotInfo'),
        ),
        migrations.AddField(
            model_name='drycell',
            name='anode_geometry',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='anode_geometry', to='cell_database.ElectrodeGeometry'),
        ),
        migrations.AddField(
            model_name='drycell',
            name='cathode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cathode', to='cell_database.CompositeLot'),
        ),
        migrations.AddField(
            model_name='drycell',
            name='cathode_geometry',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cathode_geometry', to='cell_database.ElectrodeGeometry'),
        ),
        migrations.AddField(
            model_name='drycell',
            name='geometry',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.DryCellGeometry'),
        ),
        migrations.AddField(
            model_name='drycell',
            name='separator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='separator', to='cell_database.CompositeLot'),
        ),
        migrations.AddField(
            model_name='drycell',
            name='separator_geometry',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.SeparatorGeometry'),
        ),
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, unique=True)),
                ('wet_cells', models.ManyToManyField(to='cell_database.WetCell')),
            ],
        ),
        migrations.AddField(
            model_name='compositelot',
            name='lot_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.LotInfo'),
        ),
        migrations.AddField(
            model_name='composite',
            name='components',
            field=models.ManyToManyField(to='cell_database.RatioComponent'),
        ),
        migrations.AddField(
            model_name='componentlot',
            name='lot_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.LotInfo'),
        ),
        migrations.AddField(
            model_name='component',
            name='stochiometry',
            field=models.ManyToManyField(to='cell_database.ElectrodeMaterialStochiometry'),
        ),
        migrations.AddField(
            model_name='coatinglot',
            name='lot_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cell_database.LotInfo'),
        ),
    ]
