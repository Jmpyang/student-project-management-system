from django.db import migrations


def create_default_department(apps, schema_editor):
    Department = apps.get_model("projects", "Department")
    Department.objects.using(schema_editor.connection.alias).get_or_create(
        name="Information Technology",
        defaults={
            "description": (
                "Department responsible for information technology projects "
                "and research."
            ),
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            create_default_department,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
