import java.text.SimpleDateFormat;
import java.time.format.DateTimeFormatter;
import java.util.Date;

public class CleanSimpleDateFormat {
    private static final DateTimeFormatter FORMATTER =
            DateTimeFormatter.ofPattern("yyyy-MM-dd");

    public String formatLocal() {
        SimpleDateFormat local = new SimpleDateFormat("yyyy-MM-dd");
        return local.format(new Date());
    }
}
