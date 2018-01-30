from django.apps import AppConfig
from django.db.models.signals import post_migrate


DEFAULT_COLLEGES = {
    'CS': 'Computational Sciences',
    'NS': 'Natural Sciences',
    'SS': 'Social Sciences',
    'AH': 'Arts and Humanities'
}

# DEFAULT_STUDENT_PERMISSIONS = (
#     'change_studenttutorialstatus',
#     'add_tutorial',
#     'change_tutorial',
#     'add_tutoriallink',
#     'change_tutoriallink'
# )


def post_migrate_data_creation_callback(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    student_group, exists = Group.objects.get_or_create(name='Students')
    if not exists:
        student_group.save()

    # permissions = Permission.objects.filter(codename__in=DEFAULT_STUDENT_PERMISSIONS)
    # print(permissions)
    # print(Permission.objects.all())
    # for perm in permissions:
    #     perm.group_set.add(student_group)
    #     perm.save()
    # permission_model = apps.get_model('auth.permission')
    # pset = permission_model.objects.filter(codename__in=DEFAULT_STUDENT_PERMISSIONS)
    # print(pset)
    # print(permission_model.objects.all())

    apps = kwargs['apps']
    college_model = apps.get_model('tutorials.college')
    for code, name in DEFAULT_COLLEGES.items():
        college, exists = college_model.objects.get_or_create(name=name, code=code)
        if not exists:
            college.save()


class TutorialsConfig(AppConfig):
    name = 'tutorials'

    def ready(self):
        post_migrate.connect(post_migrate_data_creation_callback, sender=self)