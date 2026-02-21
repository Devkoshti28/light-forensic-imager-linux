#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/fs.h>
#include <openssl/evp.h>
#include <stdint.h> // FIXED: Added this for uint64_t

#define BUFFER_SIZE (16 * 1024 * 1024) 

int main(int argc, char **argv) {
    setvbuf(stdout, NULL, _IONBF, 0);
    if (geteuid() != 0) { printf("ERROR: Must run as root.\n"); return 1; }
    if (argc < 3) { printf("ERROR: Usage: ./img_disk <src> <dst>\n"); return 1; }

    const char *src = argv[1];
    const char *dst = argv[2];

    int fd_in = open(src, O_RDONLY | O_NOATIME);
    if (fd_in < 0) { printf("ERROR: Failed to open source device.\n"); return 1; }
    int fd_out = open(dst, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd_out < 0) { printf("ERROR: Failed to create destination file.\n"); close(fd_in); return 1; }
    posix_fadvise(fd_in, 0, 0, POSIX_FADV_SEQUENTIAL | POSIX_FADV_NOREUSE);

    uint64_t total_size = 0;
    struct stat st;
    if (fstat(fd_in, &st) == 0 && S_ISBLK(st.st_mode)) { ioctl(fd_in, BLKGETSIZE64, &total_size); } 
    else { total_size = lseek(fd_in, 0, SEEK_END); lseek(fd_in, 0, SEEK_SET); }

    EVP_MD_CTX *md5_ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(md5_ctx, EVP_md5(), NULL);

    unsigned char *buffer;
    if (posix_memalign((void **)&buffer, 512, BUFFER_SIZE) != 0) {
        printf("ERROR: Memory allocation failed.\n");
        close(fd_in); close(fd_out); return 1;
    }

    ssize_t bytes_read;
    uint64_t current_bytes = 0;
    int update_counter = 0;

    printf("STATUS: Imaging started...\n");
    while ((bytes_read = read(fd_in, buffer, BUFFER_SIZE)) > 0) {
        if (write(fd_out, buffer, bytes_read) != bytes_read) {
            printf("ERROR: Write failure (Disk full?)\n"); break;
        }
        EVP_DigestUpdate(md5_ctx, buffer, bytes_read);
        current_bytes += bytes_read;
        if (update_counter++ % 4 == 0 || current_bytes == total_size) {
            double progress = total_size > 0 ? ((double)current_bytes / total_size) * 100.0 : 0.0;
            printf("PROGRESS: %.2f\n", progress);
        }
    }

    unsigned char md5[EVP_MAX_MD_SIZE];
    unsigned int md5_len;
    EVP_DigestFinal_ex(md5_ctx, md5, &md5_len);

    char hash_str[1024] = "Hashes | MD5: ";
    for (unsigned int i = 0; i < md5_len; i++) sprintf(hash_str + strlen(hash_str), "%02x", md5[i]);
    printf("HASH: %s\n", hash_str);
    printf("DONE\n");

    free(buffer); EVP_MD_CTX_free(md5_ctx);
    close(fd_in); fsync(fd_out); close(fd_out);
    return 0;
}
