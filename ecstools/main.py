import os
import boto3
import click
import string

from ecstools import __version__


plugin_folder = os.path.join(os.path.dirname(__file__), 'commands')


class MyCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        alpha = string.ascii_letters
        for filename in os.listdir(plugin_folder):
            if filename.startswith(tuple(alpha)) and filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns, ns)
        return ns['cli']


@click.group(cls=MyCLI)
@click.pass_context
@click.version_option(version=__version__, message=__version__)
@click.option('-p', '--profile', help='AWS profile')
@click.option('-r', '--region', help='AWS region')
def cli(ctx, region, profile):
    """AWS ECS deploy tools"""
    session = boto3.session.Session(profile_name=profile, region_name=region)
    ecs = session.client('ecs')
    ecr = session.client('ecr')
    elbv2 = session.client('elbv2')
    ctx.obj = {
        'region': region,
        'profile': profile,
        'ecs': ecs,
        'ecr': ecr,
        'elbv2': elbv2
    }
    pass


if __name__ == '__main__':
    cli()
