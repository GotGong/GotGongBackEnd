# Generated by Django 4.0.6 on 2022-07-21 07:07


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('target_date', models.DateField()),
                ('max_user_num', models.IntegerField()),
                ('rule_num', models.IntegerField()),
                ('user_num', models.IntegerField()),
                ('start_date', models.DateField(auto_now_add=True)),
                ('leader_id', models.IntegerField()),
                ('room_code', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='UserRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent_sum', models.FloatField()),
                ('refund', models.IntegerField()),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='room.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
        ),
    ]
