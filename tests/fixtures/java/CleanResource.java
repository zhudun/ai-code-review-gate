import java.io.FileInputStream;
import java.io.IOException;

public class CleanResource {
    public String read(String path) throws IOException {
        try (FileInputStream in = new FileInputStream(path)) {
            int data = in.read();
            return "data: " + data;
        }
    }
}
