#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <signal.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/ptrace.h>
#include <sys/resource.h>

#define BUFSIZE (128)
#define RES_NL (0)
#define RES_RE (1)
#define RES_TL (2)
#define RES_ML (3)

static pid_t pid;
static int time_used;
static int time_limit;
static int memory_used;
static int memory_limit;
static struct rusage ruse;
static char proc[BUFSIZE];
static char statm[BUFSIZE];

void dochild(void)
{
  struct rlimit LIM;
  LIM.rlim_cur = time_limit/1000+1;
  LIM.rlim_max = LIM.rlim_cur;
  setrlimit(RLIMIT_CPU, &LIM);

  ptrace(PTRACE_TRACEME, 0, NULL, NULL);

  setuid(2222);
  chdir("/home/cofun/tmp");
  freopen("input.txt", "r", stdin);
  freopen("output.txt", "w", stdout);
  freopen("error.txt", "w", stderr);

  nice(19);
  execl("./a.out", "./a.out", (char *)0);
  exit(0);
}

int get_memory(void)
{
  FILE *fp;
  if (!(fp = fopen(proc, "r")))
      return -1;
  fgets(statm, BUFSIZE-1, fp);
  fclose(fp);

  int size, resident, share, text, lib, data, dt;
  sscanf(statm, "%d%d%d%d%d%d%d", &size, &resident, &share, &text, &lib, &data, &dt);
  return data * (getpagesize() >> 10);
}

void done(int result, int exitcode)
{
  ptrace(PTRACE_KILL, pid, NULL, NULL);
  FILE* fr = fopen("__result.txt", "w");
/*
 * RunResult   %d  (0=>NORMAL, 1=>RE, 2=>TLE, 3=>MLE)
 * TimeUsed    %d  (MicroSecond)
 * MemoryUsed  %d  (KBytes)
 * Exitcode    %d  (Exitcode or Signal code)
 */
  fprintf(fr, "%d %d %d %d", result, time_used, memory_used, exitcode);
  fclose(fr);
  exit(0);
}

void doparent(void)
{
  sprintf(proc, "/proc/%d/statm", pid);

  int sig, status;
  while (1)
  {
    wait4(pid, &status, 0, &ruse);
    time_used  = ruse.ru_utime.tv_sec * 1000 + ruse.ru_utime.tv_usec / 1000;
    time_used += ruse.ru_stime.tv_sec * 1000 + ruse.ru_stime.tv_usec / 1000;

    if (time_used > time_limit)
      done(RES_TL, 0);
    else if (WIFEXITED(status))
      done(RES_NL, WEXITSTATUS(status));
    else if (WIFSIGNALED(status))
      done(RES_RE, WTERMSIG(status));
    else if (WIFSTOPPED(status))
    {
      sig = WSTOPSIG(status);
      if (sig == SIGTRAP)
      {
        int memory_current = get_memory();
        if (memory_current > memory_used)
          memory_used = memory_current;
        if (memory_used > memory_limit)
          done(RES_ML, 0);
      }
      else if (sig == SIGXFSZ)
        ;
      else
        done(RES_RE, sig);
    }

    ptrace(PTRACE_SYSCALL, pid, NULL, NULL);
  }
}
int main(int argc, char* argv[])
{
  if (argc < 3)
    exit(1);
  time_limit = atoi(argv[1]);
  memory_limit = atoi(argv[2]);
  if ((pid = fork()) != 0)
    doparent();
  else
    dochild();

  exit(0);
}
