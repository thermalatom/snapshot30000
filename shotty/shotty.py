import boto3
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
def instances():
    """Commands for Instances"""

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
       i.start()

    return


@instances.command('stop')
@click.option('--project', default=None,
              help='Only instances for project')

def stop_instances(project):
    "stop EC2 instances"
    instances = filter_instances(project)

    for i in instances:
       print(' Stopping {} '.format(i.id))
       i.stop()

    return


if __name__ == '__main__':
    instances()

