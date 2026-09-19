public class CleanNPE {
    public String describe(User user) {
        if (user == null) {
            return "unknown";
        }
        Address addr = user.getAddress();
        if (addr == null) {
            return "unknown";
        }
        return addr.getCity().getName();
    }
}
