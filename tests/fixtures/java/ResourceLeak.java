import java.io.FileInputStream;
import java.io.IOException;

public class ResourceLeak {
    public String read(String path) throws IOException {
        FileInputStream in = new FileInputStream(path);
        int data = in.read();
        in.close();
        return "data: " + data;
    }
}
