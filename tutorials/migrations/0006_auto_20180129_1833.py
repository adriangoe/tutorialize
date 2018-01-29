# Generated by Django 2.0.1 on 2018-01-29 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0005_auto_20180129_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studenttutorialstatus',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tutorials.Student'),
        ),
        migrations.AlterField(
            model_name='studenttutorialstatus',
            name='tutorial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tutorials.Tutorial'),
        ),
    ]
