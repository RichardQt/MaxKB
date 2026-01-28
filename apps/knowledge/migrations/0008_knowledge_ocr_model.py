# Generated migration for adding OCR model field to Knowledge

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models_provider', '0001_initial'),
        ('knowledge', '0007_remove_knowledgeworkflowversion_workflow_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledge',
            name='ocr_model',
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='ocr_knowledge',
                to='models_provider.model',
                verbose_name='OCR模型'
            ),
        ),
    ]
