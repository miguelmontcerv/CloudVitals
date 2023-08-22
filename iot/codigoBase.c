#include <HTTPClient.h>
#include <WiFi.h>

// nombre de la red y contraseña
const char *ssid = "IZZI-92A2";
const char *password = "D4AB820D92A2";

// URL de la función en Azure
String url = "https://cloudvitals.azurewebsites.net/api/counter";

HTTPClient http;

void setup()
{
 // retardo para poder abrir el Monitor Serie del IDE de Arduino
 delay(3000);
 Serial.begin(115200);
 // se conecta a la red
 WiFi.begin(ssid,password);
 Serial.print("Conectando a la red ");
 Serial.print(ssid);
 while (WiFi.status() != WL_CONNECTED)
 {
 delay(500);
 Serial.print(".");
 }
 Serial.println("");
 Serial.println("WiFi conectada");
 Serial.print("Dirección IP: ");
 Serial.println(WiFi.localIP());
}
void envia_post()
{
 http.begin(url);
 String body = "{\"numero\": 35}";
 Serial.println("Enviando POST");
 int codigo = http.POST(body);
 Serial.print("Codigo HTTP: ");
 Serial.println(codigo);
 String respuesta = http.getString();
 Serial.print("Respuesta: ");
 Serial.println(respuesta);
}

void envia_get()
{
 http.begin(url + "?num=10");
 Serial.println("Enviando GET");
 int codigo = http.GET();
 Serial.print("Codigo HTTP: ");
 Serial.println(codigo);
 String respuesta = http.getString();
 Serial.print("Respuesta: ");
 Serial.println(respuesta);
}
void loop()
{
 envia_post();
 delay(4000);
 envia_get();
 delay(3000);
}