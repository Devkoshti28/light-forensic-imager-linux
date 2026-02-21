#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <stdint.h> // This fixes the uint64_t error!

#define BUFFER_SIZE (16 * 1024 * 1024) 

// Images
unsigned char JPG_SIG[] = {0xFF, 0xD8, 0xFF};
unsigned char PNG_SIG[] = {0x89, 0x50, 0x4E, 0x47};
unsigned char GIF_SIG[] = {0x47, 0x49, 0x46, 0x38, 0x39, 0x61};
unsigned char WEBP_SIG[] = {0x52, 0x49, 0x46, 0x46}; 
// Docs & Archives
unsigned char PDF_SIG[] = {0x25, 0x50, 0x44, 0x46}; 
unsigned char DOC_SIG[] = {0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1}; 
unsigned char ZIP_SIG[] = {0x50, 0x4B, 0x03, 0x04}; 
unsigned char RAR_SIG[] = {0x52, 0x61, 0x72, 0x21, 0x1A, 0x07};
unsigned char SEVENZ_SIG[] = {0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C};
// Media
unsigned char MP3_SIG[] = {0x49, 0x44, 0x33}; 
unsigned char MP4_SIG[] = {0x66, 0x74, 0x79, 0x70}; 
unsigned char MKV_SIG[] = {0x1A, 0x45, 0xDF, 0xA3}; 
// DBs/Exe
unsigned char EXE_SIG[] = {0x4D, 0x5A}; 
unsigned char SQLITE_SIG[] = {0x53, 0x51, 0x4C, 0x69, 0x74, 0x65, 0x20, 0x66, 0x6F, 0x72, 0x6D, 0x61, 0x74, 0x20, 0x33, 0x00};

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    if (geteuid() != 0) { printf("ERROR: Must run as root.\n"); return 1; }
    if (argc < 3) { printf("ERROR: Usage: ./recover_raw <src> <out_dir>\n"); return 1; }

    const char *src = argv[1];
    const char *out_dir = argv[2];

    int fd = open(src, O_RDONLY);
    if (fd < 0) { printf("ERROR: Cannot open source image.\n"); return 1; }
    struct stat st = {0};
    if (stat(out_dir, &st) == -1) { mkdir(out_dir, 0755); }

    unsigned char *buffer = malloc(BUFFER_SIZE);
    if (!buffer) { printf("ERROR: Memory allocation failed.\n"); close(fd); return 1; }

    uint64_t total_size = lseek(fd, 0, SEEK_END);
    lseek(fd, 0, SEEK_SET);

    printf("STATUS: Scanning for signatures, code, and text files...\n");
    ssize_t bytes_read;
    uint64_t current_pos = 0;
    int files_found = 0;
    int update_counter = 0;

    while ((bytes_read = read(fd, buffer, BUFFER_SIZE)) > 0) {
        for (ssize_t i = 0; i < bytes_read - 16; i++) {
            char found_path[512];
            int found = 0;
            size_t carve_size = 0;
            size_t skip_bytes = 0; 

            if (memcmp(&buffer[i], JPG_SIG, 3) == 0) { snprintf(found_path, 512, "%s/rec_%d.jpg", out_dir, files_found++); found = 1; carve_size = 3 * 1024 * 1024; }
            else if (memcmp(&buffer[i], PNG_SIG, 4) == 0) { snprintf(found_path, 512, "%s/rec_%d.png", out_dir, files_found++); found = 1; carve_size = 3 * 1024 * 1024; }
            else if (memcmp(&buffer[i], GIF_SIG, 6) == 0) { snprintf(found_path, 512, "%s/rec_%d.gif", out_dir, files_found++); found = 1; carve_size = 2 * 1024 * 1024; }
            else if (memcmp(&buffer[i], WEBP_SIG, 4) == 0 && memcmp(&buffer[i+8], "WEBP", 4) == 0) { snprintf(found_path, 512, "%s/rec_%d.webp", out_dir, files_found++); found = 1; carve_size = 2 * 1024 * 1024; }
            else if (memcmp(&buffer[i], PDF_SIG, 4) == 0) { snprintf(found_path, 512, "%s/rec_%d.pdf", out_dir, files_found++); found = 1; carve_size = 10 * 1024 * 1024; }
            else if (memcmp(&buffer[i], DOC_SIG, 8) == 0) { snprintf(found_path, 512, "%s/rec_%d.doc", out_dir, files_found++); found = 1; carve_size = 5 * 1024 * 1024; }
            else if (memcmp(&buffer[i], ZIP_SIG, 4) == 0) { snprintf(found_path, 512, "%s/rec_%d_archive.zip", out_dir, files_found++); found = 1; carve_size = 15 * 1024 * 1024; }
            else if (memcmp(&buffer[i], RAR_SIG, 6) == 0) { snprintf(found_path, 512, "%s/rec_%d.rar", out_dir, files_found++); found = 1; carve_size = 15 * 1024 * 1024; }
            else if (memcmp(&buffer[i], SEVENZ_SIG, 6) == 0) { snprintf(found_path, 512, "%s/rec_%d.7z", out_dir, files_found++); found = 1; carve_size = 15 * 1024 * 1024; }
            else if (memcmp(&buffer[i], MP3_SIG, 3) == 0) { snprintf(found_path, 512, "%s/rec_%d.mp3", out_dir, files_found++); found = 1; carve_size = 8 * 1024 * 1024; }
            else if (memcmp(&buffer[i], MKV_SIG, 4) == 0) { snprintf(found_path, 512, "%s/rec_%d.mkv", out_dir, files_found++); found = 1; carve_size = 50 * 1024 * 1024; }
            else if (memcmp(&buffer[i+4], MP4_SIG, 4) == 0) { snprintf(found_path, 512, "%s/rec_%d.mp4", out_dir, files_found++); found = 1; carve_size = 50 * 1024 * 1024; }
            else if (memcmp(&buffer[i], SQLITE_SIG, 16) == 0) { snprintf(found_path, 512, "%s/rec_%d.sqlite", out_dir, files_found++); found = 1; carve_size = 10 * 1024 * 1024; }
            else if (memcmp(&buffer[i], EXE_SIG, 2) == 0 && buffer[i+3] == 0x00) { snprintf(found_path, 512, "%s/rec_%d.exe", out_dir, files_found++); found = 1; carve_size = 5 * 1024 * 1024; }
            
            if (!found && i + 128 < bytes_read) {
                int is_text = 1;
                for (int j = 0; j < 128; j++) {
                    unsigned char c = buffer[i+j];
                    if ((c < 32 && c != 9 && c != 10 && c != 13) || c > 126) { is_text = 0; break; }
                }
                if (is_text) {
                    carve_size = 128;
                    while (i + carve_size < bytes_read && carve_size < 2 * 1024 * 1024) {
                        unsigned char c = buffer[i + carve_size];
                        if ((c < 32 && c != 9 && c != 10 && c != 13) || c > 126) break;
                        carve_size++;
                    }
                    if (carve_size > 2048) {
                        snprintf(found_path, 512, "%s/rec_%d_txt.txt", out_dir, files_found++);
                        found = 1; skip_bytes = carve_size - 1; 
                    }
                }
            }

            if (found) {
                int out_fd = open(found_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
                if (out_fd >= 0) {
                    size_t write_len = (i + carve_size < (size_t)bytes_read) ? carve_size : ((size_t)bytes_read - i);
                    write(out_fd, &buffer[i], write_len);
                    close(out_fd);
                    i += skip_bytes; 
                }
            }
        }
        current_pos += bytes_read;
        if (update_counter++ % 4 == 0) {
            double progress = total_size > 0 ? ((double)current_pos / total_size) * 100.0 : 0.0;
            printf("PROGRESS: %.2f\n", progress);
        }
    }
    printf("PROGRESS: 100\nSTATUS: Recovery complete. Dumped %d files.\nDONE\n", files_found);
    free(buffer); close(fd);
    return 0;
}
