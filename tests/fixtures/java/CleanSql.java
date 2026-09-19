import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class CleanSql {
    public ResultSet findById(Connection conn, String userId) throws SQLException {
        String sql = "select * from users where id = ?";
        PreparedStatement ps = conn.prepareStatement(sql);
        ps.setString(1, userId);
        return ps.executeQuery();
    }
}
