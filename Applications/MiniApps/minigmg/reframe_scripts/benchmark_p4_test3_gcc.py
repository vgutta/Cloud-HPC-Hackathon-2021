import reframe as rfm
import reframe.utility.sanity as sn
import reframe.core.launchers as rcl
import hackathon as hack

@rfm.simple_test
class MiniGMGp4Test3GCC(hack.HackathonBase): ###################################################
    # Where to run the binaries 'aws:c6gn' on Arm or 'aws:c5n' on Intel
    valid_systems = ['aws:c6gn']
    # valid_prog_environs = ['*']

    # Logging Variables
    log_team_name = 'Wolfpack'
    log_app_name = 'miniGMG'
    log_test_name = 'minigmg_performance4_test3_gcc' ############################################

    # Define Execution
    # Binary to run
    executable = 'run.miniGMG'
    # Command line options to pass
    executable_opts = ['6 8 8 8 1 1 1']#, '> miniGMG.out'] ####################################
    # Where the output is written to
    # logfile = 'miniGMG.out'
    # # Store the output file (used for validation later)
    # keep_files = [logfile]


    # Parameters - Compilers - Defined as their Spack specs (use spec or hash)
    spec = parameter([    #####################################################################
        'minigmg@local%gcc@10.3.0',
        # 'minigmg@local%nvhpc@21.2',    
        # 'minigmg@local%arm@21.0.0.879',
        # 'minigmg@qidong%gcc@10.3.0',
    ])

    # Parameters - MPI / Threads - Used for scaling studies
    parallelism = parameter([ #################################################################
        { 'nodes' : 1, 'mpi' : 1, 'omp' : 1},
        # { 'nodes' : 1, 'mpi' : 1, 'omp' : 64}
    ])

    @run_before('run')
    def prepare_job(self):
        self.job.launcher.options = ['--exclusive']
        # self.job.launcher.options += ['time']

    @run_before('run')
    def set_profiler(self):
        self.proffile = 'profileP4gcc3.map'
        self.keep_files = [self.proffile]

        # self.modules.append('arm-forge@21.0')

        self.job.launcher = rcl.LauncherWrapper(self.job.launcher, 'map', ['--profile', '--output='+self.proffile])

    # @run_before('run')
    # def perf_libs_tools(self):
    #     apl_dir = 'plt_out'
    #     self.prerun_cmds.append('mkdir {0}'.format(apl_dir))
    #     self.variables['ARMPL_SUMMARY_FILEROOT'] = '$PWD/{0}/'.format(apl_dir)
    #     self.keep_files = [apl_dir]

    #     self.job.launcher.options = ['--export=ALL,LD_PRELOAD=libarmpl_mp-summarylog.so']
    #     apl_file = '{0}_{1}_apl_summary.log'.format(self.log_app_name, self.log_test_name)
    #     self.postrun_cmds.append('process_summary.py {0}/*.apl > {1}'.format(apl_dir, apl_file))
    #     self.keep_files.append(apl_file)

    # /scratch/opt/spack/linux-amzn2-graviton2/gcc-10.3.0/perf-libs-tools-git-master-ja4rifwkuuj4nw2c7usikdlomimo6yxm/lib/

    @sn.sanity_function
    def get_time_in_sec_list(self, min_list, sec_list):
        return list(x * 60 + y
                    for x, y in sn.zip(min_list, sec_list))

    # Code validation
    @run_before('sanity')
    def set_sanity_patterns(self):
        sol_regex = r'v-cycle=(\S+),\s+norm=(\S+)\s+\((\S+)\)\ndone'
        norm_list = sn.extractall(sol_regex, self.stdout, 3, float)
        self.sanity_patterns = sn.assert_lt(sn.max(norm_list), 1e-15)

        self.reference = {
            '*': {'v-cycles Time': (0, None, None, 's'),
                  'real':          (0, None, None, 's'),
                  'Total Time':       (0, None, None, 's'),}
        }

        perf_regex_vcycles = r'\s+\"\s+v-cycles\s+(\S+)'
        perf_regex_elapsed = r'(\S+)user\s+(\S+)system\s+(\S+):(\S+)elapsed\s+(\S+)\s+(\S+)'

        # elapsed_min_list = sn.extractall(perf_regex_elapsed, self.stderr, 3, float)
        # elapsed_sec_list = sn.extractall(perf_regex_elapsed, self.stderr, 4, float)

        # time_in_sec_list = self.get_time_in_sec_list(elapsed_min_list, elapsed_sec_list)

        self.perf_patterns = {
            # 'v-cycles Time': sn.extractsingle(perf_regex_vcycles, self.stdout, 1, float),
            # 'Total Time': sn.max(time_in_sec_list),
        }
