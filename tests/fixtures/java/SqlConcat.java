import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class SqlConcat {
    public ResultSet findById(Connection conn, String userId) throws SQLException {
        String sql = "select * from users where id = " + userId;
        Statement stmt = conn.createStatement();
        return stmt.executeQuery(sql);
    }
}
