import java.text.SimpleDateFormat;

public class UnsafeSimpleDateFormat {
    private static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd");

    public String format(long ts) {
        return SDF.format(ts);
    }
}
