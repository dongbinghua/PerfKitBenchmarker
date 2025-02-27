### Breaking changes:

-   Require Python 3.9+
-   The core_os os_type was removed from the Azure provider as
    [the image was deleted](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/endorsed-distros#supported-distributions-and-versions),
    -   It will be replaced by
        [Fedora Core OS](https://docs.fedoraproject.org/en-US/fedora-coreos/provisioning-azure/)
        if a public image is made available.
-   The `dpb_sparksql_benchmark` now requires passing the requested queries with
    `--dpb_sparksql_query_order`
-   AwsVirtualMachine.IMAGE_OWNER has been changed from a string to a list of
    strings to support images which have multiple owners e.g. AmazonLinux2 in
    opt-in regions.
-   Remove Ubuntu1710 from `--os_types`.
-   Remove Amazon Linux 1 from `--os_types`.
-   Changed redis_memtier_benchmark to use redis version 6 and above. Redis
    versions less than 6 are no longer supported.
-   Compressed redis_memtier samples from `--memtier_time_series` into a few
    time-to-value dictionaries, greatly reducing the number of samples produced
-   Make Ubuntu 18 the default os_type.
-   Deprecate Ubuntu 16 as it is EOL on 2021-05-01.
-   Switch to Azure CLI to MSAL. This requires updating the CLI to >= 2.30.0.
    -   See https://docs.microsoft.com/en-us/cli/azure/msal-based-azure-cli
-   Remove deprecated `--eks_zones` flags. Use `--zones` instead.
-   Deprecate CentOS Linux 8 as it is EOL on 2021-12-31.
-   `--zones` and `--extra_zones` deprecated in favor of `--zone`.

### New features:

-   Add ibmcloud as a new provider.
-   Add prefix/directory support for object storage service runs.
-   Add MaskRCNN and ReXtNet-101 to the horovod benchmark.
-   Add Bigtable Benchmarking tutorial.
-   Add ycsb_skip_run_stage argument.
-   Move PKB static website files from gh-pages branch to master branch.
-   Add UDP benchmarking to iPerf.
-   Add ability to use Intel package repos.
-   Add Ubuntu 20.04 to AWS, Azure, and GCP providers.
-   Add support for running DPB Apache Spark benchmarks on PKB provisioned VMs
-   Add support for AWS gp3 disks.
-   Add ability to use Intel compiled HPCC binaries with
    --hpcc_use_intel_compiled_hpl
-   Add OSU MPI micro-benchmarks benchmark
-   Add support for setting virtual NIC type for GCP VMs.
-   Add ability to collect /proc/meminfo data with --collect_meminfo
-   Add support for setting egress bandwidth tier for GCP VMs.
-   Add support for Azure Ultra Disk
-   Add `cloudharmony_network` benchmark
-   Add GPU PingPong benchmark.
-   Added lmod linux package.
-   Support IntelMPI 2021.x on RedHat.
-   Add TensorFlow BigQuery Connector benchmark.
-   Add gcsfuse benchmark.
-   Add MLPerf multiworker benchmark based on NVIDIA's v0.6 submission
-   Add retries to PKB.
-   Added GCE networking MTU support with --mtu.
-   Add pd extreme support to PKB.
-   Add '--delete_samples' to measure VM deletion during benchmark teardown
    phase
-   Add cloudharmony iperf benchmark to pkb.
-   Add specjbb2015 benchmark to PKB.
-   Add VM stop start benchmark.
-   Add suspend_resume benchmark.
-   Add AWS support for VM stop start benchmark.
-   Add Azure support for VM stop start benchmark.
-   Add `--os_type=debian11` support for GCP, AWS and Azure Providers.
-   Add cURL benchmark for object storage.
-   Add vbench video encoding benchmark to PKB.
-   Add Kubernetes based DPB Service for Spark
-   Add support for creating Dataproc cluster on GKE
-   Add support for TPC-DS/H benchmarks on Dataproc Serverless.
-   Add support for TPC-DS/H benchmarks on AWS Glue Job.
-   Add messaging service latency benchmark (for GCP PubSub, AWS SQS & Azure
    Service Bus).
-   Add Intel perfspect as a new trace
-   Add Ubuntu 22.04 support for GCP, AWS and Azure Providers.
-   Add support for Rocky Linux 8, CentOS Stream 8, and CentOS Stream 9 on GCP
    and AWS Providers.
-   Add support for chbench using s64da.
-   Add sysbench_memory benchmark.
-   Add support for RHEL 9 on AWS, Azure, and GCP.
-   Add GCP Optimized Rocky Linux 8 OS.
-   Add mtu to os_metadata in linux_virtual_machine.
-   Add support for TPC-DS/H benchmarks on AWS EMR Serverless.
-   Add dpb_sparksql_serverless_benchmark, which submits one job for each
    TPC-DS/H query and measures the whole job execution time, instead of only
    the query run time.
-   Add Intel MPI benchmark.
-   Add support for Azure ARM VMs.

### Enhancements:

-   Added delay_time support for delete operations in object storage service.
-   Added horovod_synthetic option for synthetic input data in ResNet/ReXtNet
    models.
-   Added support for A100 GPUs.
-   Added cuda_tookit 11.0 support.
-   Updated `retry_on_rate_limited` to false on all cluster_boot runs.
-   Add ability to apply HPC optimized script to GCE VMs with --gce_hpc_tools
-   Update the nginx benchmark.
-   Added `--before_run_pause` flag for debugging during benchmark development.
-   Report CPU vulnerabilities as a sample via the --record_cpu_vuln flag.
-   Add retry when calling MountDisk.
-   Measure time to running status of a VM in large_scale_boot benchmark.
-   SpecCPU2017 runs on Redhat, Centos7
-   Aerospike YCSB can have multiple server nodes and different client/server
    machine types.
-   HPL's configuration file customizable with flags.
-   Added Intel MPI to linux_packages.
-   Added ability to use MKL 2018.2 from Intel repos via --mkl_install_from_repo
-   Added ability to install gfortran 9 with --fortran_version=9
-   Added MSS support to netperf with `--netperf_mss`.
-   Added nfs_service.NfsExport(vm, path) to easily NFS export a directory.
-   AWS EFA works for Ubuntu1604.
-   Added support for MySQL 8.0 on VMs and minimal innodb tuning.
-   Add ability to specify version of Intel MKL with --mkl_version
-   Added intelmpi.NfsExportIntelDirectory to NFS export /opt/intel
-   Modify cloud_datastore_ycsb benchmark to execute YCSB on the same db entries
    each run instead of emptying and preloading the db every time. Can set flag
    google_datastore_repopulate=True to empty & repopulate.
-   Enhance the cpu metric collection feature for cloud bigtable benchmark: as
    long as there is a real workload (table loading is not counted), the cpu
    metrics will be collected.
-   Support wiring properties into DPB clusters with `--dpb_clusters_properties`
    in addition to `--dpb_job_properties`.
-   Add support for GCS and S3 I/O in PKB managed Spark and Hadoop clusters.
-   Update FIO workload to support extraction of common benchmark parameters
    from the scenario string.
-   Added Intel oneAPI BaseKit to packages.
-   Upgrade default CUDA version to 11.0.
-   Add support for AWS IO2 EBS instances.
-   Add support for Postgres 13 on VMs.
-   Add support to compile GCC versions on non Debian systems.
-   Add additional customization options to SPEC CPU 2017.
-   Add average utilization to the metadata of cpu metrics for Cloud Bigtable
    benchmark.
-   Add flag --ycsb_log_remote_command_output to allow enabling/disabling the
    logging of stdout & stderr from wait_for_command.
-   Add support for NFS `nconnect` mount option.
-   Add support for custom compilation of OpenJDK.
-   Add support for configuring the HBase binding to use with `--hbase_binding`.
-   Enhance the cpu utilization metrics for cloud bigtable ycsb benchmark:
    collect the cpu data for each workload (differentiated by workload_index);
    the time window estimation is also more accurate.
-   Support default subnets in --aws_subnet with `default` as value passed.
-   Add Unsupported config failure substatus for runs that are not supported by
    the cloud.
-   Add support for nodepools to `container_cluster` benchmark spec.
-   Expose GCS FUSE disk type to allow using GCS buckets as a data_disk.
-   Add support for 5th gen Azure VMs.
-   Support multiple Redis instances on the same VM and multiple client VMs.
-   Support creating autoscaled Bigtable instances.
-   Added support to allow deleting a static table in Cloud Bigtable benchmarks
    via --google_bigtable_delete_static_table.
-   Support downloading data twice in object_storage_service_benchmark.
-   Add memtier reported percentile latencies to Memtier samples metadata.
-   Add support for building multiarch Docker images.
-   Add latency capped throughput measurement mode to memtier.
-   Add Unsupported config failure substatus for Azure runs.
-   Add support for Windows 2022 and Sql server 2019 on Windows 2022
-   Add support for Redis Enterprise clustered database.
-   Support regional GKE clusters.
-   Support zonal node placement in regional Kubernetes clusters.
-   Uses the regular version of gcloud for Bigtable commands instead of beta.
-   Support logging the start timestamp of each stage.
-   Support for building GCC on Debian
-   Support for Postgres 13 on Debian
-   Add OSProvisioningTimedOut as a recognized failure mode in Azure.
-   Add support for providing initialization actions into DPB clusters with
    `--dpb_initialization_actions`
-   Add sandbox configuration fields for GKE nodepools.
-   Fetch Redis benchmark live migration times from GCP metadata server.
-   Retry table deletions in Cloud Bigtable benchmarks against a user managed
    instance and fail if the benchmark eventually fails to delete a table.
-   Add support for Snowflake on Azure External Tables
-   Fetch memtier benchmark runtime information
-   Support installing the Google Cloud Bigtable client by a given version via
    --google_bigtable_client_version and simplify dependency management.
-   Support setting --dpb_dataflow_additional_args and --dpb_dataflow_timeout
    for dpb_dataflow_provider.
-   Add support for T2A (ARM) VMs on GCE.

### Bug fixes and maintenance updates:

-   Tuned entity cleanup parameters.
-   Fix wrong unit in MLPerf benchmark.
-   Disabled TF_CUDNN_USE_AUTOTUNE for horovod benchmarks.
-   Updated default NCCL version.
-   Use a deletion task to cleanup leftover entities to avoid hitting batch
    limit.
-   Updated object storage service deleteObjects API to also return back
    object_sizes of deleted objects.
-   Fixed a bug in leftover entity deletion logic.
-   Fixed string encoding bug in netperf_pps benchmark.
-   Fix installing RedHat EPEL on GCP (rhel8,centos8) and AWS (rhel7,rhel8,
    centos8, amazonlinux2)
-   Fixed a bug in leftover entity deletion logic.
-   Use absl parameterized test case.
-   Error out if AWS EFA install fails (centos8,rhel8)
-   Added `cascadelake` as a `--gcp_min_cpu_platform` option.
-   Move CoreOS from EOL Container Linux CoreOS to Fedora CoreOS on AWS and GCP.
-   Update files to use absl/flags.
-   Tries alternate command to get boot time, fixing continuous checking for new
    time on rebooted system.
-   Correctly handle ARM processors in netperf.
-   Added --always_teardown_on_exception to allow pkb to perform teardown when
    there is exception at the provision|prepare|run|cleanup stage.
-   Updates crcmod, boto, and awscli installation to pip3.
-   Consolidates adding Ubuntu toolchain repo.
-   Moved stress_ng installation to a package.
-   Switch to using Google Cloud Build for continuous integration.
-   Fix PrettyPrintStreamPublisher to make "cpu_utilization_per_minute" show up
    in the PKB results summary for cloud bigtable benchmark.
-   Added an option to install GCP NCCL plugins.
-   Updated hbase binding (from hbase10 to hbase12) for cloud bigtable ycsb
    benchmark and hbase ycsb benchmark.
-   Added retries around spurious InvalidPlacementGroup.InUse on AWS VM create.
-   Support Redis version 6 on managed Redis datastores.
-   Updated Aerospike server release version to 4.9.0.31.
-   Updated Aerospike client release version to 4.6.21.
-   Install zlib1g-dev dependency for Aerospike client.
-   Use OMB version 4.7.1 and parse new min/max columns.
-   Added --application_default_credential_file as an alternative way to
    authenticate with Bigquery.
-   Only install pip and pip3 when they are not already installed with Python.
-   Install pip and pip3 from get-pip.py to avoid issues with old packages.
-   Fix parsing Dstat 0.7.3
-   Update hadoop version to 3.3.1
-   Updated required numpy and six versions.
-   Added `--hadoop_bin_url` flag to allow overrides for Hadoop downloads.
-   Make RunBenchmark handle KeyboardInterrupt so that benchmark specific
    resources can be cleaned up on cancellation.
-   Added --ycsb_fail_on_incomplete_loading flag to allow the test to fail fast
    in the case of table loading failures. --ycsb_insert_error_metric can be
    used to determine which metric indicates that loading failed (defaults to
    'insert Return=ERROR').
-   Enable the aggregation for "Return=NOT_FOUND" errors.
-   Added no_proxy flag for proxy settings
-   Stop attempting to delete PKB resources that failed to create.
-   Added a new user guide for bigtable walkthrough.
-   Sanitize the shell code in bigtable walkthrough doc: removing dollar sign
    and using variable expansion.
-   Added `--google_monitoring_endpoint` flag for querying a different endpoint
    than monitoring.googleapis.com. Used by `cloud_bigtable_ycsb`.
-   Update Go language binary to version 1.17.2
-   Broadens Azure quota detection parsing
-   AWS disk attaches now wait for attach, supporting io2 block express
-   Update the performance results of Bigtable testing which used a more proper
    client setup.
-   Update the runner's AWS CLI to 1.19.75.
-   Minor fix of the Bigtable benchmarking user guide.
-   Enable icelake and milan as --gcp_min_cpu_platform options.
-   Update the bigtable tutorial readme with the content of batch_testing.md.
    Unneeded files are removed.
-   Fix fio_write_against_multiple_clients additional samples and metadata.
-   Use real URLs as the links in Bigtable walkthrough doc.
-   Add option to publish to a subfolder in cloud storage publisher.
-   Parse resulting output matrix by indexing from the bottom up instead of top
    down.
-   Double build time for all cloud's docker images, for a more complex build
    script.
-   Add required dataflow option --gcpTempLocation and --region to
    gcp_dpb_dataflow provider.
-   Support taking FLAGS.dpb_jar_file and FLAGS.dpb_wordcount_additional_args
    when running wordcount benchmark.
-   Add some required types to BaseAppServiceSpec.
-   Uses nic type of GVNIC by default (instead of VIRTIO_NET) on GCE
