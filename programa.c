#include <stdio.h>
#include <stdlib.h>
#include <netcdf.h>
#include <math.h>
#include <dirent.h>
#include <string.h>
#include <time.h>

#define DIRECTORY "/home/dario/mnt/GOES16/2023/"
#define MAX_FILES 10
#define CSV_FILE "sa_2023_c.csv"

// Coordenadas del punto de estudio
#define LAT_TARGET -24.7288
#define LON_TARGET -65.4095

// Tiempo base (según GOES16: 2000-01-01 12:00:00 UTC)
#define BASE_YEAR 2000
#define BASE_MONTH 1
#define BASE_DAY 1
#define BASE_HOUR 12
#define BASE_MIN 0
#define BASE_SEC 0

// Verifica errores de NetCDF
#define ERR(e) {printf("Error: %s\n", nc_strerror(e)); exit(2);}

// Función para obtener archivos .nc de la carpeta
int get_nc_files(char files[MAX_FILES][256]) {
    DIR *dir;
    struct dirent *entry;
    int count = 0;

    if ((dir = opendir(DIRECTORY)) == NULL) {
        perror("Error abriendo directorio");
        return 0;
    }

    while ((entry = readdir(dir)) != NULL && count < MAX_FILES) {
        if (strstr(entry->d_name, ".nc") != NULL) {
            snprintf(files[count], 256, "%s%s", DIRECTORY, entry->d_name);
            count++;
        }
    }
    closedir(dir);
    return count;
}

// Convierte segundos desde 2000-01-01 12:00:00 a fecha legible
void convert_time(double seconds, char *formatted_time) {
    time_t base_time;
    struct tm t = {0};

    t.tm_year = BASE_YEAR - 1900;
    t.tm_mon = BASE_MONTH - 1;
    t.tm_mday = BASE_DAY;
    t.tm_hour = BASE_HOUR;
    t.tm_min = BASE_MIN;
    t.tm_sec = BASE_SEC;

    base_time = mktime(&t) + (time_t)seconds;
    struct tm *final_time = gmtime(&base_time);

    // Formatear la fecha en formato "YYYY-MM-DD HH:MM:SS"
    strftime(formatted_time, 25, "%Y-%m-%d %H:%M:%S", final_time);
}

// Calcula el promedio de CMI en un área de NxN alrededor del punto más cercano
float calculate_average(float *cmi_data, size_t lat_len, size_t lon_len, int min_lat, int min_lon, int N) {
    float sum = 0.0;
    int count = 0;

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            int lat_index = min_lat + i;
            int lon_index = min_lon + j;

            if (lat_index < lat_len && lon_index < lon_len) {
                sum += cmi_data[lat_index * lon_len + lon_index];
                count++;
            }
        }
    }
    return count > 0 ? sum / count : -9999;
}

// Procesa un archivo NetCDF y guarda datos en el CSV
void process_nc_file(const char *filename, FILE *csv) {
    int ncid, varid, lat_id, lon_id, time_id;
    size_t lat_len, lon_len;
    float *lat_data, *lon_data, *cmi_data;
    double time_value;
    
    if (nc_open(filename, NC_NOWRITE, &ncid)) ERR(ncid);

    if (nc_inq_varid(ncid, "latitude", &lat_id)) ERR(ncid);
    if (nc_inq_varid(ncid, "longitude", &lon_id)) ERR(ncid);
    if (nc_inq_varid(ncid, "CMI", &varid)) ERR(ncid);
    if (nc_inq_varid(ncid, "time", &time_id)) ERR(ncid);

    nc_inq_dimlen(ncid, lat_id, &lat_len);
    nc_inq_dimlen(ncid, lon_id, &lon_len);

    lat_data = (float *) malloc(lat_len * sizeof(float));
    lon_data = (float *) malloc(lon_len * sizeof(float));
    cmi_data = (float *) malloc(lat_len * lon_len * sizeof(float));

    nc_get_var_float(ncid, lat_id, lat_data);
    nc_get_var_float(ncid, lon_id, lon_data);
    nc_get_var_float(ncid, varid, cmi_data);
    nc_get_var_double(ncid, time_id, &time_value);

    int min_index_lat = 0, min_index_lon = 0;
    float min_dist = 1e9, dist;
    
    for (size_t i = 0; i < lat_len; i++) {
        for (size_t j = 0; j < lon_len; j++) {
            dist = pow(lat_data[i] - LAT_TARGET, 2) + pow(lon_data[j] - LON_TARGET, 2);
            if (dist < min_dist) {
                min_dist = dist;
                min_index_lat = i;
                min_index_lon = j;
            }
        }
    }

    // Guardar la fecha correcta
    char formatted_time[25];
    convert_time(time_value, formatted_time);

    // Calcular promedios de diferentes tamaños
    float cmi_values[15];
    int sizes[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100};

    for (int i = 0; i < 15; i++) {
        cmi_values[i] = calculate_average(cmi_data, lat_len, lon_len, min_index_lat, min_index_lon, sizes[i]);
    }

    // Guardar en el CSV
    fprintf(csv, "%s", formatted_time);
    for (int i = 0; i < 15; i++) {
        fprintf(csv, ",%.4f", cmi_values[i]);
    }
    fprintf(csv, "\n");

    nc_close(ncid);
    free(lat_data);
    free(lon_data);
    free(cmi_data);
}

int main() {
    char files[MAX_FILES][256];
    int file_count = get_nc_files(files);

    if (file_count == 0) {
        printf("No se encontraron archivos .nc en %s\n", DIRECTORY);
        return 1;
    }

    FILE *csv = fopen(CSV_FILE, "w");
    if (!csv) {
        perror("Error creando archivo CSV");
        return 1;
    }

    // Escribir encabezado del CSV
    fprintf(csv, "Fecha");
    int sizes[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 100};
    for (int i = 0; i < 15; i++) {
        fprintf(csv, ",CMI_%d", sizes[i]);
    }
    fprintf(csv, "\n");

    for (int i = 0; i < file_count; i++) {
        printf("Procesando: %s\n", files[i]);
        process_nc_file(files[i], csv);
    }

    fclose(csv);
    printf("Datos guardados en %s\n", CSV_FILE);
    return 0;
}

