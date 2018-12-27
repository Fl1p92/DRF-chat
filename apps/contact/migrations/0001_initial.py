# Generated by Django 2.1.4 on 2018-12-17 20:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ContactsList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contacts_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='contactline',
            name='contacts_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contact_lines', to='contact.ContactsList'),
        ),
        migrations.AlterUniqueTogether(
            name='contactline',
            unique_together={('contacts_list', 'contact')},
        ),
    ]
