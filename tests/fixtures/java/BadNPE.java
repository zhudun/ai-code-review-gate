public class BadNPE {
    public String describe(User user) {
        return user.getAddress().getCity().getName();
    }
}
