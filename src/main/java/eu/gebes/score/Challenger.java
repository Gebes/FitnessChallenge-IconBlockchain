package eu.gebes.score;

import foundation.icon.icx.data.Address;
import lombok.Data;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;

import java.math.BigInteger;

/**
 * * Modelclass if someone challenges you with all the details
 */
@RequiredArgsConstructor
@Data
public class Challenger {


    @NonNull BigInteger bet;
    @NonNull Address address;
    @NonNull BigInteger startTime, duration;


}
