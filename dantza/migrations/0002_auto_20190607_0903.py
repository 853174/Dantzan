# Generated by Django 2.2.1 on 2019-06-07 09:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dantza', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArropaMota',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mota', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='materialarduraduna',
            name='dantzari',
        ),
        migrations.AlterField(
            model_name='arropa',
            name='deskribapena',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='arropa',
            name='egoera',
            field=models.CharField(choices=[('ONA', 'Ona'), ('TXARRA', 'Txarra')], max_length=100),
        ),
        migrations.AlterField(
            model_name='arropa',
            name='mota',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dantza.ArropaMota'),
        ),
        migrations.AlterField(
            model_name='mailegua',
            name='arropa',
            field=models.ManyToManyField(blank=True, to='dantza.Arropa'),
        ),
        migrations.AlterField(
            model_name='mailegua',
            name='materiala',
            field=models.ManyToManyField(blank=True, to='dantza.Tresna'),
        ),
        migrations.DeleteModel(
            name='ArropaArduraduna',
        ),
        migrations.DeleteModel(
            name='MaterialArduraduna',
        ),
    ]
