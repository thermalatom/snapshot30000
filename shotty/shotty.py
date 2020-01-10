import boto3
import botocore
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')
 
def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances =  ec2.instances.all()

    return instances

@click.group()
def cli():
   """Shotty manage snapshots"""
   

@cli.group('snapshots')
def snapshots():
   """Commands for Snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
              help="list all snapshots not just latest")

def list_snapshots(project,list_all):
    "List EC2 snapshots"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                    )))
                if s.state == 'completed' and not list_all: break

    return

@cli.group('volumes')
def volumes():
   """Commands for Volumes"""

@volumes.command('list')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")

def list_volumes(project):
    "List EC2 volumes"
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
                )))

    return

@cli.group('instances')
def instances():
    """Commands for Instances"""

@instances.command('snapshot',
    help='create snapshot of all volumes')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):

    "Create volume snapshots"
    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}....".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            print("   Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description='Created by shotty')
        print("Starting {0}....".format(i.id))
        i.start()
        i.wait_until_running()

    print("Create snapshot all done")
    return


@instances.command('list')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def list_intances(project):
    "List EC2 instances"
    instances = filter_instances(project)

    for i in instances:
       tags = { t['Key']: t['Value'] for t in i.tags or [] }
       print(', '.join((
           i.id,
           i.instance_type,
           i.placement['AvailabilityZone'],
           i.state['Name'],
           i.public_dns_name,
           tags.get('Project', 'No project'))))
    return

@instances.command('start')
@click.option('--project', default=None,
              help='Only instances for project')

def start_instances(project):
    "start EC2 instances"
    instances = filter_instances(project)

    for i in instances:
       print(' Starting {} '.format(i.id))
       try:
           i.start()
       except botocore.exceptions.ClientError as e:
          print("Could not start {0}".format(i.id) + str(e))
          continue

    return


@instances.command('stop')
@click.option('--project', default=None,
              help='Only instances for project')

def stop_instances(project):
    "stop EC2 instances"
    instances = filter_instances(project)

    for i in instances:
       print(' Stopping {} '.format(i.id))
       try:
          i.stop()
       except botocore.exceptions.ClientError as e:
          print("Could not stop {0}".format(i.id) + str(e))
          continue
    return


if __name__ == '__main__':
    cli()
