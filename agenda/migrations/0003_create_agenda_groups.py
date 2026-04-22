from django.db import migrations


def create_agenda_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Agenda PTME')
    Group.objects.get_or_create(name='Agenda Adulte')


def remove_agenda_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Agenda PTME', 'Agenda Adulte']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('agenda', '0002_rendezvous_motif_prochain_rdv_and_more'),
    ]

    operations = [
        migrations.RunPython(create_agenda_groups, remove_agenda_groups),
    ]
