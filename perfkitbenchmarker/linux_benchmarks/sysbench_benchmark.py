# Copyright 2014 PerfKitBenchmarker Authors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sysbench Benchmark.

This is a set of benchmarks that measures performance of Sysbench Databases on
managed MySQL or Postgres.

As other cloud providers deliver a managed MySQL service, we will add it here.
"""


import logging
import re
import time

from absl import flags
from perfkitbenchmarker import configs
from perfkitbenchmarker import flag_util
from perfkitbenchmarker import publisher
from perfkitbenchmarker import sample
from perfkitbenchmarker import sql_engine_utils
import six


FLAGS = flags.FLAGS

# The default values for flags and BENCHMARK_CONFIG are not a recommended
# configuration for comparing sysbench performance.  Rather these values
# are set to provide a quick way to verify functionality is working.
# A broader set covering different permuations on much larger data sets
# is prefereable for comparison.
flags.DEFINE_string('sysbench_testname', 'oltp_read_write',
                    'The built in oltp lua script to run')
flags.DEFINE_integer('sysbench_tables', 4,
                     'The number of tables used in sysbench oltp.lua tests')
flags.DEFINE_integer('sysbench_table_size', 100000,
                     'The number of rows of each table used in the oltp tests')
flags.DEFINE_integer('sysbench_scale', 100,
                     'Scale parameter as used by TPCC benchmark.')
flags.DEFINE_integer('sysbench_warmup_seconds', 10,
                     'The duration of the warmup run in which results are '
                     'discarded, in seconds.')
flags.DEFINE_integer('sysbench_run_seconds', 10,
                     'The duration of the actual run in which results are '
                     'collected, in seconds.')
flag_util.DEFINE_integerlist(
    'sysbench_thread_counts',
    flag_util.IntegerList([64]),
    'array of thread counts passed to sysbench, one at a time',
    module_name=__name__)
flags.DEFINE_integer('sysbench_latency_percentile', 100,
                     'The latency percentile we ask sysbench to compute.')
flags.DEFINE_integer('sysbench_report_interval', 2,
                     'The interval, in seconds, we ask sysbench to report '
                     'results.')

BENCHMARK_DATA = {
    'sysbench-tpcc.tar.gz':
        'a116f0a6f58212b568bd339e65223eaf5ed59437503700002f016302d8a9c6ed',
}


# Parameters are defined in oltp_common.lua file
# https://github.com/akopytov/sysbench
_MAP_WORKLOAD_TO_VALID_UNIQUE_PARAMETERS = {
    'tpcc': set(['scale']),
    'oltp_write_only': set(['table_size']),
    'oltp_read_only': set(['table_size']),
    'oltp_read_write': set(['table_size'])
}


BENCHMARK_NAME = 'sysbench'
BENCHMARK_CONFIG = """
sysbench:
  description: Sysbench OLTP benchmarks.
  relational_db:
    engine: mysql
    db_spec:
      GCP:
        machine_type: db-n1-standard-16
        zone: us-central1-c
      AWS:
        machine_type: db.m4.4xlarge
        zone: us-west-1a
      Azure:
        machine_type: GP_Gen5_2
        zone: westus
    db_disk_spec:
      GCP:
        disk_size: 100
        disk_type: pd-ssd
      AWS:
        disk_size: 6144
        disk_type: gp2
      Azure:
        #From AZ command line:
        #Valid storage sizes range from minimum of 128000 MB and additional
        #increments of 128000 MB up to maximum of 1024000 MB.
        disk_size: 128
    vm_groups:
      clients:
        vm_spec:
          GCP:
            machine_type: n1-standard-16
            zone: us-central1-c
          AWS:
            machine_type: m4.4xlarge
            zone: us-west-1a
          Azure:
            machine_type: Standard_B4ms
            zone: westus
        disk_spec:
          GCP:
            disk_size: 500
            disk_type: pd-ssd
          AWS:
            disk_size: 500
            disk_type: gp2
          Azure:
            disk_size: 500
            disk_type: Premium_LRS
      servers:
        vm_spec:
          GCP:
            machine_type: n1-standard-16
            zone: us-central1-c
          AWS:
            machine_type: m4.4xlarge
            zone: us-west-1a
          Azure:
            machine_type: Standard_B4ms
            zone: westus
        disk_spec: *default_500_gb
      replications:
        vm_spec:
          GCP:
            machine_type: n1-standard-16
            zone: us-central1-b
          AWS:
            machine_type: m4.4xlarge
            zone: us-east-1a
          Azure:
            machine_type: Standard_B4ms
            zone: eastus
        disk_spec: *default_500_gb
"""

# Constants defined for Sysbench tests.
DISABLE = 'disable'
UNIFORM = 'uniform'

SECONDS_UNIT = 'seconds'


def GetConfig(user_config):
  return configs.LoadConfig(BENCHMARK_CONFIG, user_config, BENCHMARK_NAME)


def _ParseSysbenchOutput(sysbench_output):
  """Parses sysbench output.

  Extract relevant TPS and latency numbers, and populate the final result
  collection with these information.

  Specifically, we are interested in tps and latency numbers reported by each
  reporting interval.

  Args:
    sysbench_output: The output from sysbench.
  Returns:
    Three arrays, the tps, latency and qps numbers.

  """
  tps_numbers = []
  latency_numbers = []
  qps_numbers = []

  sysbench_output_io = six.StringIO(sysbench_output)
  for line in sysbench_output_io:
    # parse a line like (it's one line - broken up in the comment to fit):
    # [ 6s ] thds: 16 tps: 650.51 qps: 12938.26 (r/w/o: 9046.18/2592.05/1300.03)
    # lat (ms,99%): 40.37 err/s: 0.00 reconn/s: 0.00
    if re.match(r'^\[', line):
      match = re.search('tps: (.*?) ', line)
      if not match:
        raise ValueError(f'no tps in: {line}')
      tps_numbers.append(float(match.group(1)))
      match = re.search(r'lat \(.*?\): (.*?) ', line)
      if not match:
        raise ValueError(f'no lat in: {line}')
      latency_numbers.append(float(match.group(1)))
      match = re.search(r'qps: (.*?) \(.*?\) ', line)
      if not match:
        raise ValueError(f'no qps in: {line}')
      qps_numbers.append(float(match.group(1)))
      if line.startswith('SQL statistics:'):
        break

  return tps_numbers, latency_numbers, qps_numbers


def AddMetricsForSysbenchOutput(
    sysbench_output, results, metadata, metric_prefix=''):
  """Parses sysbench output.

  Extract relevant TPS and latency numbers, and populate the final result
  collection with these information.

  Specifically, we are interested in tps and latency numbers reported by each
  reporting interval.

  Args:
    sysbench_output: The output from sysbench.
    results: The dictionary to store results based on sysbench output.
    metadata: The metadata to be passed along to the Samples class.
    metric_prefix:  An optional prefix to append to each metric generated.
  """
  tps_numbers, latency_numbers, qps_numbers = (
      _ParseSysbenchOutput(sysbench_output))

  tps_metadata = metadata.copy()
  tps_metadata.update({metric_prefix + 'tps': tps_numbers})
  tps_sample = sample.Sample(metric_prefix + 'tps_array', -1,
                             'tps', tps_metadata)

  latency_metadata = metadata.copy()
  latency_metadata.update({metric_prefix + 'latency': latency_numbers})
  latency_sample = sample.Sample(metric_prefix + 'latency_array', -1, 'ms',
                                 latency_metadata)

  qps_metadata = metadata.copy()
  qps_metadata.update({metric_prefix + 'qps': qps_numbers})
  qps_sample = sample.Sample(metric_prefix + 'qps_array', -1, 'qps',
                             qps_metadata)

  results.append(tps_sample)
  results.append(latency_sample)
  results.append(qps_sample)


# TODO(chunla) Move this to engine specific module
def _GetSysbenchConnectionParameter(client_vm_query_tools):
  """Get Sysbench connection parameter."""
  connection_string = ''
  if client_vm_query_tools.ENGINE_TYPE == sql_engine_utils.MYSQL:
    connection_string = (
        '--mysql-host={0} --mysql-user={1} --mysql-password="{2}" ').format(
            client_vm_query_tools.connection_properties.endpoint,
            client_vm_query_tools.connection_properties.database_username,
            client_vm_query_tools.connection_properties.database_password)
  elif client_vm_query_tools.ENGINE_TYPE == sql_engine_utils.POSTGRES:
    connection_string = (
        '--pgsql-host={0} --pgsql-user={1} --pgsql-password="{2}" '
        '--pgsql-port=5432').format(
            client_vm_query_tools.connection_properties.endpoint,
            client_vm_query_tools.connection_properties.database_username,
            client_vm_query_tools.connection_properties.database_password)
  return connection_string


# TODO(chunla) Move this to engine specific module
def _GetCommonSysbenchOptions(benchmark_spec):
  """Get Sysbench options."""
  db = benchmark_spec.relational_db
  engine = sql_engine_utils.GetDbEngineType(FLAGS.managed_db_engine)
  result = []

  # Ignore possible mysql errors
  # https://github.com/actiontech/dble/issues/458
  # https://callisto.digital/posts/tools/using-sysbench-to-benchmark-mysql-5-7/
  if engine == sql_engine_utils.MYSQL:
    result += [
        '--db-ps-mode=%s' % DISABLE,
        # Error 1205: Lock wait timeout exceeded
        # Could happen when we overload the database
        '--mysql-ignore-errors=1213,1205,1020,2013',
        '--db-driver=mysql'
    ]
  elif engine == sql_engine_utils.POSTGRES:
    # TODO(chunla): might need to add pgsql-db
    result += [
        '--db-driver=pgsql',
    ]

  result += [db.client_vm_query_tools.GetSysbenchConnectionString()]
  return result


def _GetSysbenchCommand(duration, benchmark_spec, sysbench_thread_count):
  """Returns the sysbench command as a string."""
  if duration <= 0:
    raise ValueError('Duration must be greater than zero.')

  run_cmd_tokens = ['nice',  # run with a niceness of lower priority
                    '-15',   # to encourage cpu time for ssh commands
                    'sysbench',
                    FLAGS.sysbench_testname,
                    '--tables=%d' % FLAGS.sysbench_tables,
                    ('--table_size=%d' % FLAGS.sysbench_table_size
                     if _IsValidFlag('table_size') else ''),
                    ('--scale=%d' % FLAGS.sysbench_scale
                     if _IsValidFlag('scale') else ''),
                    '--rand-type=%s' % UNIFORM,
                    '--threads=%d' % sysbench_thread_count,
                    '--percentile=%d' % FLAGS.sysbench_latency_percentile,
                    '--report-interval=%d' % FLAGS.sysbench_report_interval,
                    '--max-requests=0',
                    '--time=%d' % duration]
  run_cmd = ' '.join(run_cmd_tokens +
                     _GetCommonSysbenchOptions(benchmark_spec) +
                     ['run'])
  return run_cmd


def _IssueSysbenchCommand(vm, duration, benchmark_spec, sysbench_thread_count):
  """Issues a sysbench run command given a vm and a duration.

      Does nothing if duration is <= 0

  Args:
    vm: The test VM to issue command to.
    duration: the duration of the sysbench run.
    benchmark_spec: The benchmark specification. Contains all data that is
                    required to run the benchmark.
    sysbench_thread_count: count of number of threads to use in --threads
                           parameter to sysbench.

  Returns:
    stdout, stderr: the result of the command.
  """
  stdout = ''
  stderr = ''
  if duration > 0:
    run_cmd = _GetSysbenchCommand(
        duration,
        benchmark_spec,
        sysbench_thread_count)
    stdout, stderr = vm.RobustRemoteCommand(run_cmd, timeout=duration + 60)
    logging.info('Sysbench results: \n stdout is:\n%s\nstderr is\n%s',
                 stdout, stderr)

  return stdout, stderr


def _RunSysbench(
    vm, metadata, benchmark_spec, sysbench_thread_count):
  """Runs the Sysbench OLTP test.

  Args:
    vm: The VM that will issue the sysbench test.
    metadata: The PKB metadata to be passed along to the final results.
    benchmark_spec: The benchmark specification. Contains all data that is
                    required to run the benchmark.
    sysbench_thread_count: The number of client threads that will connect.

  Returns:
    Results: A list of results of this run.
  """
  results = []

  # Now run the sysbench OLTP test and parse the results.
  # First step is to run the test long enough to cover the warmup period
  # as requested by the caller. Second step is the 'real' run where the results
  # are parsed and reported.

  warmup_seconds = FLAGS.sysbench_warmup_seconds
  if warmup_seconds > 0:
    logging.info('Sysbench warm-up run, duration is %d', warmup_seconds)
    _IssueSysbenchCommand(vm, warmup_seconds, benchmark_spec,
                          sysbench_thread_count)

  run_seconds = FLAGS.sysbench_run_seconds
  logging.info('Sysbench real run, duration is %d', run_seconds)
  stdout, _ = _IssueSysbenchCommand(vm, run_seconds, benchmark_spec,
                                    sysbench_thread_count)

  logging.info('\n Parsing Sysbench Results...\n')
  AddMetricsForSysbenchOutput(stdout, results, metadata)

  return results


def _GetDatabaseSize(benchmark_spec):
  """Get the size of the database in MB."""
  db = benchmark_spec.relational_db
  db_engine = sql_engine_utils.GetDbEngineType(FLAGS.managed_db_engine)
  stdout = None
  if db_engine == sql_engine_utils.MYSQL:
    stdout, _ = db.client_vm_query_tools.IssueSqlCommand(
        'SELECT table_schema AS \'Database\', '
        'ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) '
        'AS \'Size (MB)\' '
        'FROM information_schema.TABLES '
        'GROUP BY table_schema; ')
    logging.info('Query database size results: \n%s', stdout)
    # example stdout is tab delimited but shown here with spaces:
    # Database  Size (MB)
    # information_schema  0.16
    # mysql 5.53
    # performance_schema  0.00
    # sbtest  0.33
    size_mb = 0
    for line in stdout.splitlines()[1:]:
      _, word_size_mb = line.split()
      size_mb += float(word_size_mb)

  elif db_engine == sql_engine_utils.POSTGRES:
    stdout, _ = db.client_vm_query_tools.IssueSqlCommand(
        r'SELECT pg_database_size('
        '\'sbtest\''
        ')/1024/1024')
    size_mb = int(stdout.split()[2])

  return size_mb


def _PrepareSysbench(client_vm, benchmark_spec):
  """Prepare the Sysbench OLTP test with data loading stage.

  Args:
    client_vm: The client VM that will issue the sysbench test.
    benchmark_spec: The benchmark specification. Contains all data that is
                    required to run the benchmark.
  Returns:
    results: A list of results of the data loading step.
  """

  _InstallLuaScriptsIfNecessary(client_vm)

  results = []

  db = benchmark_spec.relational_db

  stdout, stderr = db.client_vm_query_tools.IssueSqlCommand(
      'create database sbtest;')

  logging.info('sbtest db created, stdout is %s, stderr is %s', stdout, stderr)
  # Provision the Sysbench test based on the input flags (load data into DB)
  # Could take a long time if the data to be loaded is large.
  data_load_start_time = time.time()
  # Data loading is write only so need num_threads less than or equal to the
  # amount of tables - capped at 64 threads for when number of tables
  # gets very large.
  num_threads = min(FLAGS.sysbench_tables, 64)

  data_load_cmd_tokens = ['nice',  # run with a niceness of lower priority
                          '-15',   # to encourage cpu time for ssh commands
                          'sysbench',
                          FLAGS.sysbench_testname,
                          '--tables=%d' % FLAGS.sysbench_tables,
                          ('--table_size=%d' % FLAGS.sysbench_table_size
                           if _IsValidFlag('table_size') else ''),
                          ('--scale=%d' % FLAGS.sysbench_scale
                           if _IsValidFlag('scale') else ''),
                          '--threads=%d' % num_threads]
  data_load_cmd = ' '.join(data_load_cmd_tokens +
                           _GetCommonSysbenchOptions(benchmark_spec) +
                           ['prepare'])

  # Sysbench output is in stdout, but we also get stderr just in case
  # something went wrong.
  stdout, stderr = client_vm.RobustRemoteCommand(data_load_cmd)
  load_duration = time.time() - data_load_start_time
  logging.info('It took %d seconds to finish the data loading step',
               load_duration)
  logging.info('data loading results: \n stdout is:\n%s\nstderr is\n%s',
               stdout, stderr)

  db.sysbench_db_size_MB = _GetDatabaseSize(benchmark_spec)
  metadata = CreateMetadataFromFlags(db)

  results.append(sample.Sample(
      'sysbench data load time',
      load_duration,
      SECONDS_UNIT,
      metadata))

  return results


def _InstallLuaScriptsIfNecessary(vm):
  if FLAGS.sysbench_testname == 'tpcc':
    vm.InstallPreprovisionedBenchmarkData(
        BENCHMARK_NAME, ['sysbench-tpcc.tar.gz'], '~')
    vm.RemoteCommand('tar -zxvf sysbench-tpcc.tar.gz')


def _IsValidFlag(flag):
  return (flag in
          _MAP_WORKLOAD_TO_VALID_UNIQUE_PARAMETERS[FLAGS.sysbench_testname])


def CreateMetadataFromFlags(db):
  """Create meta data with all flags for sysbench."""
  metadata = {
      'sysbench_testname': FLAGS.sysbench_testname,
      'sysbench_tables': FLAGS.sysbench_tables,
      'sysbench_table_size': FLAGS.sysbench_table_size,
      'sysbench_scale': FLAGS.sysbench_scale,
      'sysbench_warmup_seconds': FLAGS.sysbench_warmup_seconds,
      'sysbench_run_seconds': FLAGS.sysbench_run_seconds,
      'sysbench_latency_percentile': FLAGS.sysbench_latency_percentile,
      'sysbench_report_interval': FLAGS.sysbench_report_interval,
      'sysbench_db_size_MB': db.sysbench_db_size_MB,
  }
  return metadata


def UpdateBenchmarkSpecWithFlags(benchmark_spec):
  """Updates benchmark_spec with flags that are used in the run stage."""
  benchmark_spec.tables = FLAGS.sysbench_tables
  benchmark_spec.sysbench_table_size = FLAGS.sysbench_table_size


def Prepare(benchmark_spec):
  """Prepare the MySQL DB Instances, configures it.

     Prepare the client test VM, installs SysBench, configures it.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that is
        required to run the benchmark.
  """
  # We would like to always cleanup server side states.
  # If we don't set this, our cleanup function will only be called when the VM
  # is static VM, but we have server side states to cleanup regardless of the
  # VM type.

  benchmark_spec.always_call_cleanup = True

  client_vm = benchmark_spec.vm_groups['clients'][0]

  UpdateBenchmarkSpecWithFlags(benchmark_spec)

  # Setup common test tools required on the client VM
  client_vm.Install('sysbench')

  prepare_results = _PrepareSysbench(client_vm, benchmark_spec)
  print(prepare_results)


def Run(benchmark_spec):
  """Run the sysbench benchmark and publish results.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that is
        required to run the benchmark.

  Returns:
    Results.
  """
  logging.info('Start benchmarking, '
               'Cloud Provider is %s.', FLAGS.cloud)
  client_vm = benchmark_spec.vms[0]
  db = benchmark_spec.relational_db

  for thread_count in FLAGS.sysbench_thread_counts:
    metadata = CreateMetadataFromFlags(db)
    metadata['sysbench_thread_count'] = thread_count
    # The run phase is common across providers. The VMs[0] object contains all
    # information and states necessary to carry out the run.
    run_results = _RunSysbench(client_vm, metadata, benchmark_spec,
                               thread_count)
    print(run_results)
    publisher.PublishRunStageSamples(benchmark_spec, run_results)

  # all results have already been published
  return []


def Cleanup(benchmark_spec):
  """Clean up benchmark related states on server and client.

  Args:
    benchmark_spec: The benchmark specification. Contains all data that is
        required to run the benchmark.
  """
  del benchmark_spec
