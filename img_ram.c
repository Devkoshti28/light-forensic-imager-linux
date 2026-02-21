#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    if (geteuid() != 0) { printf("ERROR: Must run as root.\n"); return 1; }
    if (argc < 3) { printf("ERROR: Usage: ./img_ram <dst> <lime_ko_path>\n"); return 1; }

    const char *dst = argv[1];
    const char *lime_ko = argv[2];

    char cmd[512];
    system("rmmod lime 2>/dev/null");
    snprintf(cmd, sizeof(cmd), "insmod %s path=\"%s\" format=raw", lime_ko, dst);
    
    printf("STATUS: Attempting to inject LiME module...\n");
    int ret = system(cmd);
    
    if (ret == 0) {
        printf("PROGRESS: 100\n");
        printf("STATUS: RAM Capture Complete.\n");
        system("rmmod lime 2>/dev/null");
    } else { 
        printf("ERROR: Failed to load LiME module. Ensure lime.ko matches your exact kernel version.\n"); 
    }
    printf("DONE\n");
    return 0;
}
