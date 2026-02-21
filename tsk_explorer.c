#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    if (argc < 3) { printf("ERROR: Invalid arguments for explorer.\n"); return 1; }

    char cmd[1024];

    if (strcmp(argv[1], "--partitions") == 0) {
        snprintf(cmd, sizeof(cmd), "mmls '%s'", argv[2]); 
        FILE *fp = popen(cmd, "r");
        if (!fp) return 1;
        char line[2048];
        printf("PARTITION_START\n");
        while (fgets(line, sizeof(line), fp) != NULL) { printf("%s", line); }
        pclose(fp);
        printf("PARTITION_END\nDONE\n");
    } 
    else if (strcmp(argv[1], "--list") == 0 && argc >= 4) {
        snprintf(cmd, sizeof(cmd), "fls -o %s -r -p '%s'", argv[3], argv[2]); 
        FILE *fp = popen(cmd, "r");
        if (!fp) { printf("ERROR: Failed to run fls.\n"); return 1; }
        char line[2048];
        printf("STATUS: Extracting File System structure...\n");
        while (fgets(line, sizeof(line), fp) != NULL) { printf("FILE_ENTRY: %s", line); }
        pclose(fp);
        printf("STATUS: Scan Complete.\nDONE\n");
    } 
    else if (strcmp(argv[1], "--extract") == 0 && argc >= 6) {
        snprintf(cmd, sizeof(cmd), "icat -o %s '%s' '%s' > '%s'", argv[3], argv[2], argv[4], argv[5]);
        if (system(cmd) == 0) { printf("STATUS: Extracted successfully.\n"); } 
        else { printf("ERROR: icat failed.\n"); }
        printf("DONE\n");
    } 
    else if (strcmp(argv[1], "--meta") == 0 && argc >= 5) {
        snprintf(cmd, sizeof(cmd), "istat -o %s '%s' '%s'", argv[3], argv[2], argv[4]);
        printf("META_START\n");
        system(cmd);
        printf("\nMETA_END\nDONE\n");
    } 
    else if (strcmp(argv[1], "--preview") == 0 && argc >= 6) {
        snprintf(cmd, sizeof(cmd), "icat -o %s '%s' '%s' | head -c 4096 > '%s'", argv[3], argv[2], argv[4], argv[5]);
        system(cmd);
        printf("DONE\n");
    } 
    else {
        printf("ERROR: Unknown TSK flag.\n");
    }
    return 0;
}
