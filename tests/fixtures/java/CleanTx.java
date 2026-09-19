import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CleanTx {

    @Transactional(rollbackFor = Exception.class)
    public void placeOrder(Order order) {
        try {
            inventory.reserve(order);
            payment.charge(order);
        } catch (Exception e) {
            log.error("failed to place order", e);
            throw e;
        }
    }
}
